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


class SubjectsYAMLReader(BaseReader):
    """Subjects YAML Reader."""

    def __init__(self, *args, options=None, **kwargs):
        """Constructor."""
        self._options = options or {}
        super().__init__(*args, **kwargs)

    def _iter(self, data, *args, **kwargs):
        """Iterates over a dictionary and returns a dictionary per element."""
        for entry in data:
            yield entry

    def read(self, item=None, *args, **kwargs):
        """Read the YAML file."""
        import yaml

        with open(self._options["filename"], "r") as f:
            data = yaml.safe_load(f)
            yield from self._iter(data=data, *args, **kwargs)


class OAIPMHSubjectsReader(BaseReader):
    # not implemented
    pass


class SubjectsYAMLTransformer(BaseTransformer):
    """Subjects Transformer."""

    def apply(self, stream_entry, **kwargs):
        """Transform the data to the invenio subjects format."""
        record = stream_entry.entry
        subject_entry = {}
        print("Transforming data to invenio subjects format...")

        subject_entry["subject"] = record.get("subject")
        subject_entry["identifier"] = record.get("identifier")
        subject_entry["scheme"] = record.get("scheme")
        subject_entry["parent"] = record.get("parent")

        return subject_entry


class SubjectsServiceWriter(ServiceWriter):
    """Subjects Service Writer."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super().__init__(*args, **kwargs)

    def write(self, data, *args, **kwargs):
        """Write the data to the service."""


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
