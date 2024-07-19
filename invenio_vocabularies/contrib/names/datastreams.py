# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names datastreams, transformers, writers and readers."""

import io
import tarfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

import s3fs
from flask import current_app
from invenio_records.dictutils import dict_lookup

from ...datastreams.errors import TransformerError
from ...datastreams.readers import BaseReader, SimpleHTTPReader
from ...datastreams.transformers import BaseTransformer
from ...datastreams.writers import ServiceWriter


class OrcidDataSyncReader(BaseReader):
    """ORCiD Data Sync Reader."""

    def _fetch_orcid_data(self, orcid_to_sync, fs, bucket):
        """Fetches a single ORCiD record from S3."""
        # The ORCiD file key is located in a folder which name corresponds to the last three digits of the ORCiD
        suffix = orcid_to_sync[-3:]
        key = f"{suffix}/{orcid_to_sync}.xml"
        try:
            with fs.open(f"s3://{bucket}/{key}", "rb") as f:
                file_response = f.read()
            return file_response
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
        date_format = "%Y-%m-%d %H:%M:%S.%f"
        date_format_no_millis = "%Y-%m-%d %H:%M:%S"

        last_sync = datetime.now() - timedelta(
            days=current_app.config["VOCABULARIES_ORCID_SYNC_DAYS"]
        )

        file_content = fileobj.read().decode("utf-8")

        for line in file_content.splitlines()[1:]:  # Skip the header line
            elements = line.split(",")
            orcid = elements[0]

            # Lambda file is ordered by last modified date
            last_modified_str = elements[3]
            try:
                last_modified_date = datetime.strptime(last_modified_str, date_format)
            except ValueError:
                last_modified_date = datetime.strptime(
                    last_modified_str, date_format_no_millis
                )

            if last_modified_date >= last_sync:
                yield orcid
            else:
                break

    def _iter(self, orcids, fs):
        """Iterates over the ORCiD records yielding each one."""
        with ThreadPoolExecutor(
            max_workers=current_app.config["VOCABULARIES_ORCID_SYNC_MAX_WORKERS"]
        ) as executor:
            futures = [
                executor.submit(
                    self._fetch_orcid_data,
                    orcid,
                    fs,
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
        fs = s3fs.S3FileSystem(
            key=current_app.config["VOCABULARIES_ORCID_ACCESS_KEY"],
            secret=current_app.config["VOCABULARIES_ORCID_SECRET_KEY"],
        )
        # Read the file from S3
        with fs.open("s3://orcid-lambda-file/last_modified.csv.tar", "rb") as f:
            tar_content = f.read()

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

        yield from self._iter(orcids_to_sync, fs)


class OrcidHTTPReader(SimpleHTTPReader):
    """ORCiD HTTP Reader."""

    def __init__(self, *args, test_mode=True, **kwargs):
        """Constructor."""
        if test_mode:
            origin = "https://sandbox.orcid.org/{id}"
        else:
            origin = "https://orcid.org/{id}"

        super().__init__(origin, *args, **kwargs)


class OrcidTransformer(BaseTransformer):
    """Transforms an ORCiD record into a names record."""

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
            "type": "orcid-data-sync",
        },
        {"type": "xml"},
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
