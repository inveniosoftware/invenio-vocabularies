# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
# Copyright (C) 2024 California Institute of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Funders datastreams, transformers, writers and readers."""

from flask import current_app
from invenio_i18n import lazy_gettext as _

from ...datastreams.writers import ServiceWriter
from ..common.ror.datastreams import RORTransformer


class FundersServiceWriter(ServiceWriter):
    """Funders service writer."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        service_or_name = kwargs.pop("service_or_name", "funders")
        super().__init__(service_or_name=service_or_name, *args, **kwargs)

    def _entry_id(self, entry):
        """Get the id from an entry."""
        return entry["id"]


class FundersRORTransformer(RORTransformer):
    """Funders ROR Transformer."""

    def __init__(
        self, *args, vocab_schemes=None, funder_fundref_doi_prefix=None, **kwargs
    ):
        """Constructor."""
        if vocab_schemes is None:
            vocab_schemes = current_app.config.get("VOCABULARIES_FUNDER_SCHEMES")
        if funder_fundref_doi_prefix is None:
            funder_fundref_doi_prefix = current_app.config.get(
                "VOCABULARIES_FUNDER_DOI_PREFIX"
            )
        super().__init__(
            *args,
            vocab_schemes=vocab_schemes,
            funder_fundref_doi_prefix=funder_fundref_doi_prefix,
            **kwargs,
        )


VOCABULARIES_DATASTREAM_READERS = {}
"""Funders datastreams writers."""

VOCABULARIES_DATASTREAM_WRITERS = {
    "funders-service": FundersServiceWriter,
}
"""Funders datastreams writers."""


VOCABULARIES_DATASTREAM_TRANSFORMERS = {
    "ror-funders": FundersRORTransformer,
}
"""Funders datastreams transformers."""


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
            "type": "ror-funders",
        },
    ],
    "writers": [
        {
            "type": "async",
            "args": {
                "writer": {
                    "type": "funders-service",
                }
            },
        }
    ],
}
"""Data Stream configuration.

An origin is required for the reader.
"""
