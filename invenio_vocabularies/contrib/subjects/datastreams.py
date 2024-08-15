# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 University of Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names datastreams, transformers, writers and readers."""

from invenio_access.permissions import system_identity
from invenio_i18n import lazy_gettext as _

from ...datastreams.writers import ServiceWriter


class SubjectsServiceWriter(ServiceWriter):
    """Subjects Service Writer."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        service_or_name = kwargs.pop("service_or_name", "subjects")
        super().__init__(service_or_name=service_or_name, *args, **kwargs)

    def _entry_id(self, entry):
        """Get the id from an entry."""
        return entry["id"]


VOCABULARIES_DATASTREAM_READERS = {}
"""Subjects Data Streams readers."""

VOCABULARIES_DATASTREAM_TRANSFORMERS = {}
"""Subjects Data Streams transformers."""

VOCABULARIES_DATASTREAM_WRITERS = {
    "subjects-service": SubjectsServiceWriter,
}
"""Subjects Data Streams writers."""

DATASTREAM_CONFIG = {
    "readers": [
        {"type": "yaml"},
    ],
    "writers": [
        {
            "type": "subjects-service",
        }
    ],
}
"""Data Stream configuration."""
