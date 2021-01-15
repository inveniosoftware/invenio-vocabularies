# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary components."""

from invenio_records_resources.services.records.components import \
    ServiceComponent


class VocabularyTypeComponent(ServiceComponent):
    """Service component for metadata."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject vocabulary type to the record."""
        record.vocabulary_type_id = data.get("vocabulary_type_id", None)

    def update(self, identity, data=None, record=None, **kwargs):
        """Inject vocabulary type to the record."""
        record.vocabulary_type_id = data.get("vocabulary_type_id", None)
