# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
# Copyright (C) 2024 California Institute of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Funders datastreams, transformers, writers and readers."""

from idutils import normalize_ror
from invenio_access.permissions import system_identity
from invenio_i18n import lazy_gettext as _

from ...datastreams.errors import TransformerError
from ...datastreams.transformers import BaseTransformer
from ...datastreams.writers import ServiceWriter
from .config import funder_fundref_doi_prefix, funder_schemes


class FundersServiceWriter(ServiceWriter):
    """Funders service writer."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        service_or_name = kwargs.pop("service_or_name", "funders")
        super().__init__(service_or_name=service_or_name, *args, **kwargs)

    def _entry_id(self, entry):
        """Get the id from an entry."""
        return entry["id"]


class RORTransformer(BaseTransformer):
    """Transforms a JSON ROR record into a funders record."""

    def apply(self, stream_entry, **kwargs):
        """Applies the transformation to the stream entry."""
        record = stream_entry.entry
        funder = {}
        funder["title"] = {}

        funder["id"] = normalize_ror(record.get("id"))
        if not funder["id"]:
            raise TransformerError(_("Id not found in ROR entry."))

        aliases = []
        acronym = None
        for name in record.get("names"):
            lang = name.get("lang", "en")
            if "ror_display" in name["types"]:
                funder["name"] = name["value"]
            if "label" in name["types"]:
                funder["title"][lang] = name["value"]
            if "alias" in name["types"]:
                aliases.append(name["value"])
            if "acronym" in name["types"]:
                # The first acronyn goes in acronym field to maintain
                # compatability with existing data structure
                if not acronym:
                    acronym = name["value"]
                else:
                    aliases.append(name["value"])
        if acronym:
            funder["acronym"] = acronym
        if aliases:
            funder["aliases"] = aliases

        # ror_display is required and should be in every entry
        if not funder["name"]:
            raise TransformerError(
                _("Name with type ror_display not found in ROR entry.")
            )

        # This only gets the first location, to maintain compatability
        # with existing data structure
        location = record.get("locations", [{}])[0].get("geonames_details", {})
        funder["country"] = location.get("country_code")
        funder["country_name"] = location.get("country_name")
        funder["location_name"] = location.get("name")

        funder["types"] = record.get("types")

        status = record.get("status")
        funder["status"] = status

        # The ROR is always listed in identifiers, expected by serialization
        funder["identifiers"] = [{"identifier": funder["id"], "scheme": "ror"}]
        valid_schemes = set(funder_schemes.keys())
        fund_ref = "fundref"
        valid_schemes.add(fund_ref)
        for identifier in record.get("external_ids"):
            scheme = identifier["type"]
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
                "regex": "_schema_v2\\.json$",
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
                "identity": system_identity,
            },
        }
    ],
}
"""Data Stream configuration.

An origin is required for the reader.
"""
