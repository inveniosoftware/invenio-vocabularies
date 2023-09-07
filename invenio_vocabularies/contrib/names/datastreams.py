# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names datastreams, transformers, writers and readers."""

from invenio_access.permissions import system_identity
from invenio_records.dictutils import dict_lookup

from ...datastreams.errors import TransformerError
from ...datastreams.readers import SimpleHTTPReader
from ...datastreams.transformers import BaseTransformer
from ...datastreams.writers import ServiceWriter


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
                "regex": ".xml$",
            },
        },
        {"type": "xml"},
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
