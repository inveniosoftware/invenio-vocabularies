# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
# Copyright (C) 2024 California Institute of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Affiliations datastreams, transformers, writers and readers."""

from flask import current_app

from ...datastreams.errors import TransformerError, WriterError
from ...datastreams.transformers import BaseTransformer
from ...datastreams.writers import ServiceWriter
from ..common.ror.datastreams import RORTransformer


class AffiliationsServiceWriter(ServiceWriter):
    """Affiliations service writer."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        service_or_name = kwargs.pop("service_or_name", "affiliations")
        super().__init__(service_or_name=service_or_name, *args, **kwargs)

    def _entry_id(self, entry):
        """Get the id from an entry."""
        return entry["id"]


class AffiliationsRORTransformer(RORTransformer):
    """Affiliations ROR Transformer."""

    def __init__(
        self, *args, vocab_schemes=None, funder_fundref_doi_prefix=None, **kwargs
    ):
        """Constructor."""
        if vocab_schemes is None:
            vocab_schemes = current_app.config.get("VOCABULARIES_AFFILIATION_SCHEMES")
        super().__init__(
            *args,
            vocab_schemes=vocab_schemes,
            funder_fundref_doi_prefix=funder_fundref_doi_prefix,
            **kwargs,
        )


class OpenAIREOrganizationTransformer(BaseTransformer):
    """OpenAIRE Organization Transformer."""

    def apply(self, stream_entry, **kwargs):
        """Applies the transformation to the stream entry."""
        record = stream_entry.entry

        if "id" not in record:
            raise TransformerError([f"No id for: {record}"])

        if not record["id"].startswith("openorgs____::"):
            raise TransformerError([f"Not valid OpenAIRE OpenOrgs id for: {record}"])

        if "pid" not in record:
            raise TransformerError([f"No alternative identifiers for: {record}"])

        organization = {}

        for pid in record["pid"]:
            if pid["scheme"] == "ROR":
                organization["id"] = pid["value"].removeprefix("https://ror.org/")
            elif pid["scheme"] == "PIC":
                organization["identifiers"] = [
                    {
                        "scheme": "pic",
                        "identifier": pid["value"],
                    }
                ]

        stream_entry.entry = organization
        return stream_entry


class OpenAIREAffiliationsServiceWriter(ServiceWriter):
    """OpenAIRE Affiliations service writer."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        service_or_name = kwargs.pop("service_or_name", "affiliations")
        # Here we only update and we do not insert, since OpenAIRE data is used to augment existing affiliations
        # (with PIC identifiers) and is not used to create new affiliations.
        super().__init__(
            service_or_name=service_or_name, insert=False, update=True, *args, **kwargs
        )

    def _entry_id(self, entry):
        """Get the id from an entry."""
        return entry["id"]

    def write(self, stream_entry, *args, **kwargs):
        """Writes the input entry using a given service."""
        entry = stream_entry.entry

        return super().write(stream_entry, *args, **kwargs)

    def write_many(self, stream_entries, *args, **kwargs):
        """Writes the input entries using a given service."""
        return super().write_many(stream_entries, *args, **kwargs)


VOCABULARIES_DATASTREAM_READERS = {}
"""Affiliations datastream readers."""

VOCABULARIES_DATASTREAM_WRITERS = {
    "affiliations-service": AffiliationsServiceWriter,
    "openaire-affiliations-service": OpenAIREAffiliationsServiceWriter,
}
"""Affiliations datastream writers."""

VOCABULARIES_DATASTREAM_TRANSFORMERS = {
    "ror-affiliations": AffiliationsRORTransformer,
    "openaire-organization": OpenAIREOrganizationTransformer,
}
"""Affiliations datastream transformers."""


DATASTREAM_CONFIG = {
    "readers": [
        {
            "type": "zip",
            "args": {
                "regex": "_schema_v2\\.json$",
            },
        },
        {"type": "json"},
    ],
    "transformers": [
        {
            "type": "ror-affiliations",
        },
    ],
    "writers": [
        {
            "type": "async",
            "args": {
                "writer": {
                    "type": "affiliations-service",
                }
            },
        }
    ],
}
"""Data Stream configuration.

An origin is required for the reader.
"""

DATASTREAM_CONFIG_OPENAIRE = {
    "readers": [
        {"type": "openaire-http", "args": {"tar_href": "/organization.tar"}},
        {
            "type": "tar",
            "args": {
                "regex": "\\.json.gz$",
                "mode": "r",
            },
        },
        {"type": "gzip"},
        {"type": "jsonl"},
    ],
    "transformers": [
        {
            "type": "openaire-organization",
        },
    ],
    "writers": [
        {
            "type": "async",
            "args": {
                "writer": {
                    "type": "openaire-affiliations-service",
                }
            },
        }
    ],
}
"""Alternative Data Stream configuration for OpenAIRE Affiliations."""
