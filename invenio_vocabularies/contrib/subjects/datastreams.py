# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names datastreams, transformers, writers and readers."""

import idutils
from invenio_access.permissions import system_identity
from invenio_i18n import lazy_gettext as _
from invenio_records.dictutils import dict_lookup

from ...datastreams.errors import TransformerError
from ...datastreams.readers import BaseReader, SimpleHTTPReader
from ...datastreams.transformers import BaseTransformer
from ...datastreams.writers import ServiceWriter
from .config import subject_schemes


class YAMLTransformer(BaseTransformer):
    """Transforms a YAML record into a subjects record."""

    def __init__(self, *args, vocab_schemes=None, **kwargs):
        """Initializes the transformer."""
        self.vocab_schemes = vocab_schemes
        super().__init__(*args, **kwargs)

    def apply(self, stream_entry, **kwargs):
        """Transform the data to the invenio subjects format."""
        record = stream_entry.entry
        subject = {}
        subject["subject"] = {}

        subject["id"] = record["id"]
        if not subject["id"]:
            raise TransformerError(_("Id not found in YAML entry."))

        subject["scheme"] = record["scheme"]
        for lang in record["subject"].keys():
            subject["subject"][lang] = record["subject"][lang]

        subject["synonyms"] = []
        for synonym in record["synonyms"]:
            subject["synonyms"].append(synonym)

        if self.vocab_schemes:
            valid_schemes = set(self.vocab_schemes.keys())
        else:
            valid_schemes = set()
        subject["identifiers"] = []
        for identifier in record["identifiers"]:
            schemes = idutils.detect_identifier_schemes(identifier)
            for scheme in schemes:
                if scheme in valid_schemes:
                    subject["identifiers"].append(
                        {
                            "identifier": identifier,
                            "scheme": scheme,
                        }
                    )
                    break

        return subject


class SubjectsServiceWriter(ServiceWriter):
    """Subjects Service Writer."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        service_or_name = kwargs.pop("service_or_name", "subjects")
        super().__init__(*args, **kwargs)

    def _entry_id(self, entry):
        """Get the id from an entry."""
        return entry["id"]


VOCABULARIES_DATASTREAM_TRANSFORMERS = {
    "yaml-vocabulary": YAMLTransformer,
}
"""Yaml Data Streams transformers."""


VOCABULARIES_DATASTREAM_WRITERS = {
    "subjects-service": SubjectsServiceWriter,
}
"""Subjects Data Streams transformers."""


DATASTREAM_CONFIG = {
    "readers": [
        {"type": "yaml"},
    ],
    "transformers": [
        {
            "type": "yaml-vocabulary",
            "args": {
                "vocab_schemes": subject_schemes,
            },
        },
    ],
    "writers": [
        {
            "type": "subjects-service",
            "args": {
                "identity": system_identity,
            },
        }
    ],
}
"""Data Stream configuration."""
