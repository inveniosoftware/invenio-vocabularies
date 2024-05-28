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
        {
            "type": "ror",
            "args": {
                "vocab_schemes": funder_schemes,
                "funder_fundref_doi_prefix": funder_fundref_doi_prefix,
            },
        },
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
