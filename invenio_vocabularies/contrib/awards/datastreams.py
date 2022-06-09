# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Awards datastreams, transformers, writers and readers."""

from flask_babelex import lazy_gettext as _
from invenio_access.permissions import system_identity

from ...datastreams.errors import TransformerError
from ...datastreams.transformers import BaseTransformer
from ...datastreams.writers import ServiceWriter
from .config import awards_ec_ror_id, awards_openaire_funders_mapping


class AwardsServiceWriter(ServiceWriter):
    """Funders service writer."""

    def _entry_id(self, entry):
        """Get the id from an entry."""
        return entry["id"]


class OpenAIREProjectTransformer(BaseTransformer):
    """Transforms an OpenAIRE project record into an award record."""

    def apply(self, stream_entry, **kwargs):
        """Applies the transformation to the stream entry."""
        record = stream_entry.entry
        award = {}

        code = record["code"]
        openaire_funder_prefix = record["id"].split("::")[0].split("|")[1]
        funder_id = awards_openaire_funders_mapping.get(openaire_funder_prefix)
        if funder_id is None:
            raise TransformerError(
                _(
                    "Unknown OpenAIRE funder prefix {openaire_funder_prefix}".format(
                        openaire_funder_prefix=openaire_funder_prefix
                    )
                )
            )

        award["id"] = f"{funder_id}::{code}"

        identifiers = []
        if funder_id == awards_ec_ror_id:
            identifiers.append(
                {
                    "identifier": f"https://cordis.europa.eu/projects/{code}",
                    "scheme": "url",
                }
            )
        elif record.get("websiteurl"):
            identifiers.append(
                {"identifier": record.get("websiteurl"), "scheme": "url"}
            )

        if identifiers:
            award["identifiers"] = identifiers

        award["number"] = code
        award["title"] = {"en": record["title"]}
        award["funder"] = {"id": funder_id}
        acronym = record.get("acronym")
        if acronym:
            award["acronym"] = acronym

        stream_entry.entry = award
        return stream_entry


VOCABULARIES_DATASTREAM_TRANSFORMERS = {
    "openaire-award": OpenAIREProjectTransformer,
}
"""ORCiD Data Streams transformers."""

VOCABULARIES_DATASTREAM_WRITERS = {
    "awards-service": AwardsServiceWriter,
}
"""ORCiD Data Streams transformers."""

DATASTREAM_CONFIG = {
    "readers": [
        {
            "type": "tar",
            "args": {
                "regex": ".json.gz$",
                "mode": "r",
            },
        },
        {"type": "gzip"},
        {"type": "jsonl"},
    ],
    "transformers": [
        {"type": "openaire-award"},
    ],
    "writers": [
        {
            "type": "awards-service",
            "args": {
                "service_or_name": "awards",
                "identity": system_identity,
            },
        }
    ],
}
"""Data Stream configuration.

An origin is required for the reader.
"""
