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
from ...datastreams.readers import SimpleHTTPReader, BaseReader
from ...datastreams.transformers import BaseTransformer
from ...datastreams.writers import ServiceWriter


class SubjectsYAMLTransformer(BaseTransformer):
    """Subjects Transformer."""

    def apply(self, stream_entry, **kwargs):
        """Transform the data to the invenio subjects format."""
        record = stream_entry.entry
        subject_entry = {}

        subject_entry["subject"] = record.get("subject")
        subject_entry["id"] = record.get("id")
        subject_entry["scheme"] = record.get("scheme")

        return subject_entry


class SubjectsServiceWriter(ServiceWriter):
    """Subjects Service Writer."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super().__init__(*args, **kwargs)

    def write(self, data, *args, **kwargs):
        """Write the data to the service."""

        raise NotImplementedError("Not implemented yet.")


VOCABULARIES_DATASTREAM_TRANSFORMERS = {
    "yaml-vocabulary": SubjectsYAMLTransformer,
}
"""ROR Data Streams transformers."""


VOCABULARIES_DATASTREAM_WRITERS = {
    "subjects-service": SubjectsServiceWriter,
}
"""Funders Data Streams transformers."""


DATASTREAM_CONFIG = {
    "readers": [
        {"type": "yaml"},
    ],
    "transformers": [
        {"type": "yaml-vocabulary"},
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
"""Data Stream configuration.

"""
