# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2025 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names datastreams, transformers, writers and readers."""

import csv
import io
import tarfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextvars import copy_context
from datetime import timedelta
from itertools import islice
from pathlib import Path

import arrow
import regex as re
from flask import current_app
from invenio_access.permissions import system_identity
from werkzeug.utils import cached_property

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

    def _fetch_orcid_data(self, app, orcid_to_sync, bucket):
        """Fetches a single ORCiD record from S3."""
        # The ORCiD file key is located in a folder which name corresponds to the last three digits of the ORCiD
        suffix = orcid_to_sync[-3:]
        key = f"{suffix}/{orcid_to_sync}.xml"
        app.logger.debug(f"Fetching ORCiD record: {key} from bucket: {bucket}")
        try:
            # Potential improvement: use the a XML jax parser to avoid loading the whole file in memory
            # and choose the sections we need to read (probably the summary)
            return self.s3_client.read_file(f"s3://{bucket}/{key}")
        except Exception:
            app.logger.exception(f"Failed to fetch ORCiD record: {key}")

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
        try:
            content = io.TextIOWrapper(fileobj, encoding="utf-8")
            csv_reader = csv.DictReader(content)

            for row in csv_reader:  # Skip the header line
                orcid = row["orcid"]

                # Lambda file is ordered by last modified date
                last_modified_str = row["last_modified"]
                try:
                    last_modified_date = arrow.get(last_modified_str, date_format)
                except arrow.parser.ParserError:
                    last_modified_date = arrow.get(
                        last_modified_str, date_format_no_millis
                    )

                if last_modified_date < last_sync:
                    current_app.logger.debug(
                        f"Skipping ORCiD {orcid} (last modified: {last_modified_date})"
                    )
                    break
                current_app.logger.debug(f"Yielding ORCiD {orcid} for sync.")
                yield orcid
        finally:
            fileobj.close()

    def _iter(self, orcids):
        """Iterates over the ORCiD records yielding each one."""
        with ThreadPoolExecutor(
            max_workers=current_app.config["VOCABULARIES_ORCID_SYNC_MAX_WORKERS"]
        ) as executor:
            app = current_app._get_current_object()
            # futures is a dictionary where the key is the ORCID value and the item is the Future object
            # Flask does not propagate app/request context to new threads, so `copy_context().run`
            # ensures the current instantianted contextvars (such as job_context) is preserved in each thread.
            futures = {
                orcid: executor.submit(
                    copy_context().run,  # Required to pass the context to the thread
                    self._fetch_orcid_data,
                    app,  # Pass the Flask app to the thread
                    orcid,
                    current_app.config["VOCABULARIES_ORCID_SUMMARIES_BUCKET"],
                )
                for orcid in orcids
            }

            for orcid in list(futures.keys()):
                try:
                    result = futures[orcid].result()
                    if result:
                        current_app.logger.debug(
                            f"Successfully fetched ORCiD record: {orcid}"
                        )
                        yield result
                except Exception:
                    current_app.logger.exception(
                        f"Error processing ORCiD record: {orcid}"
                    )
                finally:
                    # Explicitly release memory, as we don't need the future anymore.
                    # This is mostly required because as long as we keep a reference to the future
                    # (in the above futures dict), the garbage collector won't collect it
                    # and it will keep the memory allocated.
                    del futures[orcid]

    def read(self, item=None, *args, **kwargs):
        """Streams the ORCiD lambda file, process it to get the ORCiDS to sync and yields it's data."""
        # Read the file from S3
        tar_content = self.s3_client.read_file(
            "s3://orcid-lambda-file/last_modified.csv.tar"
        )
        current_app.logger.info("Fetching ORCiD lambda file")
        # Opens tar file and process it
        with tarfile.open(fileobj=io.BytesIO(tar_content)) as tar:
            # Iterate over each member (file or directory) in the tar file
            for member in tar.getmembers():
                # Extract the file
                extracted_file = tar.extractfile(member)
                if extracted_file:
                    current_app.logger.info(f"Processing lambda file: {member.name}")
                    # Process the file and get the ORCiDs to sync
                    orcids_to_sync = set(self._process_lambda_file(extracted_file))

                    # Close the file explicitly after processing
                    extracted_file.close()

                    # Process ORCIDs in smaller batches
                    for orcid_batch in self._chunked_iter(
                        orcids_to_sync, batch_size=100
                    ):
                        yield from self._iter(orcid_batch)

    def _chunked_iter(self, iterable, batch_size):
        """Yield successive chunks of a given size."""
        it = iter(iterable)
        while chunk := list(islice(it, batch_size)):
            current_app.logger.debug(f"Processing batch of size {len(chunk)}.")
            yield chunk


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
"""Regex to filter out names with punctuation, symbols, numbers and emojis."""


class OrcidOrgToAffiliationMapper:
    """Default ORCiD Org ID to affiliation ID mapper."""

    def __init__(self, org_ids_mapping=None, org_ids_mapping_file=None):
        """Constructor."""
        self._org_ids_mapping = org_ids_mapping
        self._org_ids_mapping_file = org_ids_mapping_file

    @cached_property
    def org_ids_mapping(self):
        """Mapping of ORCiD org IDs to affiliation IDs."""
        org_ids_mapping_file = self._org_ids_mapping_file or current_app.config.get(
            "VOCABULARIES_ORCID_ORG_IDS_MAPPING_PATH"
        )
        if org_ids_mapping_file:
            org_ids_mapping_file = Path(org_ids_mapping_file)
            # If the path is relative, prepend the instance path
            if not org_ids_mapping_file.is_absolute():
                org_ids_mapping_file = (
                    Path(current_app.instance_path) / org_ids_mapping_file
                )
            with open(org_ids_mapping_file) as fin:
                result = {}
                reader = csv.reader(fin)

                # Check if the first row is a header
                org_scheme, org_id, aff_id = next(reader)
                if org_scheme.lower() != "org_scheme":
                    result[(org_scheme, org_id)] = aff_id

                for org_scheme, org_id, aff_id in reader:
                    result[(org_scheme, org_id)] = aff_id

                return result

        return self._org_ids_mapping or {}

    def __call__(self, org_scheme, org_id):
        """Map an ORCiD org ID to an affiliation ID."""
        # By default we know that ROR IDs are linkable
        if org_scheme == "ROR":
            return org_id.split("/")[-1]
        # Otherwise see if we have a mapping from other schemes to an affiliation ID
        return self.org_ids_mapping.get((org_scheme, org_id))


class OrcidTransformer(BaseTransformer):
    """Transforms an ORCiD record into a names record."""

    def __init__(
        self,
        *args,
        names_exclude_regex=DEFAULT_NAMES_EXCLUDE_REGEX,
        org_id_to_affiliation_id_func=None,
        **kwargs,
    ) -> None:
        """Constructor."""
        self._names_exclude_regex = names_exclude_regex
        self._org_id_to_affiliation_id_func = (
            org_id_to_affiliation_id_func or OrcidOrgToAffiliationMapper()
        )
        super().__init__()

    def org_id_to_affiliation_id(self, org_scheme, org_id):
        """Convert and ORCiD org ID to a linkable affiliation ID."""
        return self._org_id_to_affiliation_id_func(org_scheme, org_id)

    def apply(self, stream_entry, **kwargs):
        """Applies the transformation to the stream entry."""
        current_app.logger.debug("Applying transformation to stream entry.")
        record = stream_entry.entry
        person = record["person"]
        orcid_id = record["orcid-identifier"]["path"]

        name = person.get("name")
        if name is None:
            raise TransformerError(
                f"Name not found in ORCiD entry for ORCiD ID: {orcid_id}."
            )
        if name.get("family-name") is None:
            raise TransformerError(
                f"Family name not found in ORCiD entry for ORCiD ID: {orcid_id}."
            )

        if not self._is_valid_name(name["given-names"] + name["family-name"]):
            raise TransformerError(
                f"Invalid characters in name for ORCiD ID: {orcid_id}."
            )

        entry = {
            "id": orcid_id,
            "given_name": name.get("given-names"),
            "family_name": name.get("family-name"),
            "identifiers": [{"scheme": "orcid", "identifier": orcid_id}],
            "affiliations": self._extract_affiliations(record),
        }

        stream_entry.entry = entry
        current_app.logger.debug(f"Transformed entry: {entry}")
        return stream_entry

    def _is_valid_name(self, name):
        """Check whether the name passes the regex."""
        if not self._names_exclude_regex:
            return True
        return not bool(re.search(self._names_exclude_regex, name, re.UNICODE | re.V1))

    def _extract_affiliations(self, record):
        """Extract affiliations from the ORCiD record."""
        current_app.logger.debug("Extracting affiliations from ORCiD record.")
        result = []
        try:
            employments = (
                record.get("activities-summary", {})
                .get("employments", {})
                .get("affiliation-group", [])
            )

            # If there are single values, the XML to dict, doesn't wrap them in a list
            if isinstance(employments, dict):
                employments = [employments]

            # Remove the "employment-summary" nesting
            employments = [
                employment.get("employment-summary", {}) for employment in employments
            ]

            for employment in employments:
                terminated = employment.get("end-date")
                if terminated:
                    continue

                org = employment["organization"]
                aff_id = self._extract_affiliation_id(org)

                # Skip adding if the ID already exists in result
                if aff_id and any(aff.get("id") == aff_id for aff in result):
                    continue

                # Skip adding if the name exists in result with no ID
                if any(
                    aff.get("name") == org["name"] and "id" not in aff for aff in result
                ):
                    continue

                aff = {"name": org["name"]}
                if aff_id:
                    aff["id"] = aff_id

                result.append(aff)
        except Exception:
            current_app.logger.error("Error extracting affiliations.")
        return result

    def _extract_affiliation_id(self, org):
        """Extract the affiliation ID from an ORCiD organization."""
        dis_org = org.get("disambiguated-organization")
        if not dis_org:
            return

        aff_id = None
        org_id = dis_org.get("disambiguated-organization-identifier")
        org_scheme = dis_org.get("disambiguation-source")
        if org_id and org_scheme:
            aff_id = self.org_id_to_affiliation_id(org_scheme, org_id)
        return aff_id


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
                    "args": {"update": True},
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
