# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Awards datastreams, transformers, writers and readers."""

from invenio_access.permissions import system_identity
from invenio_i18n import lazy_gettext as _

from ...datastreams.errors import TransformerError
from ...datastreams.transformers import BaseTransformer
from ...datastreams.writers import ServiceWriter
from .config import awards_ec_ror_id, awards_openaire_funders_mapping


class AwardsServiceWriter(ServiceWriter):
    """Funders service writer."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        service_or_name = kwargs.pop("service_or_name", "awards")
        super().__init__(service_or_name=service_or_name, *args, **kwargs)

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

        # The `id` should follow the format `sourcePrefix::md5(localId)` where `sourcePrefix` is 12 characters long.
        # See: https://graph.openaire.eu/docs/data-model/pids-and-identifiers#identifiers-in-the-graph
        #
        # The format of `id` in the full OpenAIRE Graph Dataset (https://doi.org/10.5281/zenodo.3516917)
        # follows this format (e.g. 'abc_________::0123456789abcdef0123456789abcdef').
        # However, the format of `id` in the new collected projects dataset (https://doi.org/10.5281/zenodo.6419021)
        # does not follow this format, and has a `40|` prefix (e.g. '40|abc_________::0123456789abcdef0123456789abcdef').
        #
        # The number '40' corresponds to the entity types 'Project'.
        # See: https://ec.europa.eu/research/participants/documents/downloadPublic?documentIds=080166e5a3a1a213&appId=PPGMS
        # See: https://graph.openaire.eu/docs/5.0.0/data-model/entities/project#id
        openaire_funder_prefix = record["id"].split("::", 1)[0].split("|", 1)[-1]

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

        funding = next(iter(record.get("funding", [])), None)
        if funding:
            funding_stream_id = funding.get("funding_stream", {}).get("id", "")
            # Example funding stream ID: `EC::HE::HORIZON-AG-UN`. We need the `EC`
            # string, i.e. the second "part" of the identifier.
            program = next(iter(funding_stream_id.split("::")[1:2]), "")
            if program:
                award["program"] = program

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
                "regex": "\\.json.gz$",
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
                "identity": system_identity,
            },
        }
    ],
}
"""Data Stream configuration.

An origin is required for the reader.
"""
