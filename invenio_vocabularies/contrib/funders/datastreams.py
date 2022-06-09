# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Funders datastreams, transformers, writers and readers."""

from flask_babelex import lazy_gettext as _
from idutils import normalize_ror
from invenio_access.permissions import system_identity

from ...datastreams.errors import TransformerError
from ...datastreams.transformers import BaseTransformer
from ...datastreams.writers import ServiceWriter
from .config import funder_fundref_doi_prefix, funder_schemes


class FundersServiceWriter(ServiceWriter):
    """Funders service writer."""

    def _entry_id(self, entry):
        """Get the id from an entry."""
        return entry["id"]


class RORTransformer(BaseTransformer):
    """Transforms a JSON ROR record into a funders record."""

    def apply(self, stream_entry, **kwargs):
        """Applies the transformation to the stream entry."""
        record = stream_entry.entry
        funder = {}

        funder["id"] = normalize_ror(record.get("id"))
        if not funder["id"]:
            raise TransformerError(_(f"Id not found in ROR entry."))

        funder["name"] = record.get("name")
        if not funder["name"]:
            raise TransformerError(_(f"Name not found in ROR entry."))

        country_code = record.get("country", {}).get("country_code")
        if country_code:
            funder["country"] = country_code

        funder["title"] = {"en": funder["name"]}
        for label in record.get("labels", []):
            funder["title"][label["iso639"]] = label["label"]

        funder["identifiers"] = []
        valid_schemes = set(funder_schemes.keys())
        fund_ref = "fundref"
        valid_schemes.add(fund_ref)
        for scheme, identifier in record.get("external_ids", {}).items():
            scheme = scheme.lower()
            if scheme in valid_schemes:
                value = identifier.get("preferred") or identifier.get("all")[0]
                if scheme == fund_ref:
                    value = f"{funder_fundref_doi_prefix}/{value}"
                    scheme = "doi"

                funder["identifiers"].append(
                    {
                        "identifier": value,
                        "scheme": scheme,
                    }
                )

        stream_entry.entry = funder
        return stream_entry


VOCABULARIES_DATASTREAM_TRANSFORMERS = {
    "ror-funder": RORTransformer,
}
"""ROR Data Streams transformers."""


VOCABULARIES_DATASTREAM_WRITERS = {
    "funders-service": FundersServiceWriter,
}
"""Funders Data Streams transformers."""


DATASTREAM_CONFIG = {
    "readers": [
        {
            "type": "zip",
            "args": {
                "regex": ".json$",
            },
        },
        {"type": "json"},
    ],
    "transformers": [
        {"type": "ror-funder"},
    ],
    "writers": [
        {
            "type": "funders-service",
            "args": {
                "service_or_name": "funders",
                "identity": system_identity,
            },
        }
    ],
}
"""Data Stream configuration.

An origin is required for the reader.
"""
