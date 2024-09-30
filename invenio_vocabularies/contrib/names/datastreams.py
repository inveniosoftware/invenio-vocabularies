# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names datastreams, transformers, writers and readers."""

import csv
import io
import tarfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta

import arrow
import regex as re
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_records.dictutils import dict_lookup

from invenio_vocabularies.contrib.names.s3client import S3OrcidClient

from ...datastreams.errors import TransformerError
from ...datastreams.readers import BaseReader, SimpleHTTPReader
from ...datastreams.transformers import BaseTransformer
from ...datastreams.writers import ServiceWriter


class OrcidDataSyncReader(BaseReader):
    """ORCiD Data Sync Reader."""

    def __init__(self, origin=None, mode="r", since=None, *args, **kwargs):
        """Constructor.

        :param origin: Data source (e.g. filepath).
                       Can be none in case of piped readers.
        """
        super().__init__(origin=origin, mode=mode, *args, **kwargs)
        self.s3_client = S3OrcidClient()
        self.since = since

    def _fetch_orcid_data(self, orcid_to_sync, bucket):
        """Fetches a single ORCiD record from S3."""
        # The ORCiD file key is located in a folder which name corresponds to the last three digits of the ORCiD
        suffix = orcid_to_sync[-3:]
        key = f"{suffix}/{orcid_to_sync}.xml"
        try:
            return self.s3_client.read_file(f"s3://{bucket}/{key}")
        except Exception as e:
            # TODO: log
            return None

    def _process_lambda_file(self, fileobj):
        """Process the ORCiD lambda file and returns a list of ORCiDs to sync.

        The decoded fileobj looks like the following:
        orcid, path, date_created, last_modified
        0000-0001-5109-3700, http://orcid.org/0000-0001-5109-3700, 2014-08-02 15:00:00.000,2021-08-02 15:00:00.000

        Yield ORCiDs to sync until the last sync date is reached.
        """
        date_format = "YYYY-MM-DD HH:mm:ss.SSSSSS"
        date_format_no_millis = "YYYY-MM-DD HH:mm:ss"
        time_shift = current_app.config["VOCABULARIES_ORCID_SYNC_SINCE"]
        if self.since:
            time_shift = self.since
        last_sync = arrow.now() - timedelta(**time_shift)

        file_content = fileobj.read().decode("utf-8")

        csv_reader = csv.DictReader(file_content.splitlines())

        for row in csv_reader:  # Skip the header line
            orcid = row["orcid"]

            # Lambda file is ordered by last modified date
            last_modified_str = row["last_modified"]
            try:
                last_modified_date = arrow.get(last_modified_str, date_format)
            except arrow.parser.ParserError:
                last_modified_date = arrow.get(last_modified_str, date_format_no_millis)

            if last_modified_date < last_sync:
                break
            yield orcid

    def _iter(self, orcids):
        """Iterates over the ORCiD records yielding each one."""
        with ThreadPoolExecutor(
            max_workers=current_app.config["VOCABULARIES_ORCID_SYNC_MAX_WORKERS"]
        ) as executor:
            futures = [
                executor.submit(
                    self._fetch_orcid_data,
                    orcid,
                    current_app.config["VOCABULARIES_ORCID_SUMMARIES_BUCKET"],
                )
                for orcid in orcids
            ]
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    yield result

    def read(self, item=None, *args, **kwargs):
        """Streams the ORCiD lambda file, process it to get the ORCiDS to sync and yields it's data."""
        # Read the file from S3
        tar_content = self.s3_client.read_file(
            "s3://orcid-lambda-file/last_modified.csv.tar"
        )

        orcids_to_sync = []
        # Opens tar file and process it
        with tarfile.open(fileobj=io.BytesIO(tar_content)) as tar:
            # Iterate over each member (file or directory) in the tar file
            for member in tar.getmembers():
                # Extract the file
                extracted_file = tar.extractfile(member)
                if extracted_file:
                    # Process the file and get the ORCiDs to sync
                    orcids_to_sync.extend(self._process_lambda_file(extracted_file))

        yield from self._iter(orcids_to_sync)


class OrcidHTTPReader(SimpleHTTPReader):
    """ORCiD HTTP Reader."""

    def __init__(self, *args, test_mode=True, **kwargs):
        """Constructor."""
        if test_mode:
            origin = "https://sandbox.orcid.org/{id}"
        else:
            origin = "https://orcid.org/{id}"

        super().__init__(origin, *args, **kwargs)


DEFAULT_NAMES_EXCLUDE_REGEX = r"[\p{P}\p{S}\p{Nd}\p{No}\p{Emoji}--,.()\-']"
"""Regex to filter out names with punctuations, symbols, decimal numbers and emojis."""


class OrcidTransformer(BaseTransformer):
    """Transforms an ORCiD record into a names record."""

    def __init__(
        self, *args, names_exclude_regex=DEFAULT_NAMES_EXCLUDE_REGEX, **kwargs
    ) -> None:
        """Constructor."""
        self._names_exclude_regex = names_exclude_regex
        super().__init__()

    def _is_valid_name(self, name):
        """Check whether the name passes the regex."""
        if not self._names_exclude_regex:
            return True
        return not bool(re.search(self._names_exclude_regex, name, re.UNICODE | re.V1))

    def apply(self, stream_entry, **kwargs):
        """Applies the transformation to the stream entry."""
        record = stream_entry.entry
        person = record["person"]
        orcid_id = record["orcid-identifier"]["path"]

        name = person.get("name")
        if name is None:
            raise TransformerError(f"Name not found in ORCiD entry.")
        if name.get("family-name") is None:
            raise TransformerError(f"Family name not found in ORCiD entry.")

        if not self._is_valid_name(name["given-names"] + name["family-name"]):
            raise TransformerError(f"Invalid characters in name.")

        entry = {
            "id": orcid_id,
            "given_name": name.get("given-names"),
            "family_name": name.get("family-name"),
            "identifiers": [{"scheme": "orcid", "identifier": orcid_id}],
            "affiliations": [],
        }

        try:
            employments = dict_lookup(
                record, "activities-summary.employments.affiliation-group"
            )
            if isinstance(employments, dict):
                employments = [employments]
            history = set()
            for employment in employments:
                terminated = employment["employment-summary"].get("end-date")
                affiliation = dict_lookup(
                    employment,
                    "employment-summary.organization.name",
                )
                if affiliation not in history and not terminated:
                    history.add(affiliation)
                    entry["affiliations"].append({"name": affiliation})
        except Exception:
            pass

        stream_entry.entry = entry
        return stream_entry


class NamesServiceWriter(ServiceWriter):
    """Names service writer."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        service_or_name = kwargs.pop("service_or_name", "names")
        super().__init__(service_or_name=service_or_name, *args, **kwargs)

    def _entry_id(self, entry):
        """Get the id from an entry."""
        return entry["id"]


VOCABULARIES_DATASTREAM_READERS = {
    "orcid-http": OrcidHTTPReader,
    "orcid-data-sync": OrcidDataSyncReader,
}


VOCABULARIES_DATASTREAM_TRANSFORMERS = {
    "orcid": OrcidTransformer,
}
"""ORCiD Data Streams transformers."""


VOCABULARIES_DATASTREAM_WRITERS = {
    "names-service": NamesServiceWriter,
}
"""ORCiD Data Streams transformers."""


DATASTREAM_CONFIG = {
    "readers": [
        {
            "type": "tar",
            "args": {
                "regex": "\\.xml$",
            },
        },
        {
            "type": "xml",
            "args": {
                "root_element": "record",
            },
        },
    ],
    "transformers": [{"type": "orcid"}],
    "writers": [
        {
            "type": "names-service",
            "args": {
                "identity": system_identity,
            },
        }
    ],
}
"""ORCiD Data Stream configuration.

An origin is required for the reader.
"""

# TODO: Used on the jobs and should be set as a "PRESET" (naming to be defined)
ORCID_PRESET_DATASTREAM_CONFIG = {
    "readers": [
        {
            "type": "orcid-data-sync",
        },
        {
            "type": "xml",
            "args": {
                "root_element": "record",
            },
        },
    ],
    "transformers": [{"type": "orcid"}],
    "writers": [
        {
            "type": "async",
            "args": {
                "writer": {
                    "type": "names-service",
                }
            },
        }
    ],
    "batch_size": 1000,
    "write_many": True,
}
"""ORCiD Data Stream configuration.

An origin is required for the reader.
"""
