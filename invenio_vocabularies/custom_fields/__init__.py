# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom Fields for InvenioRDM."""

from flask import g
from invenio_vocabularies.resources.serializer import VocabularyL10NItemSchema
from marshmallow import fields

from invenio_records_resources.services.custom_fields.base import BaseCF
from invenio_records_resources.records.systemfields import PIDListRelation, PIDRelation
from ..proxies import current_service


class VocabularyCF(BaseCF):
    """Vocabulary custom field.

    Supporting common vocabulary structure.
    """

    def __init__(self, name, vocabulary_id, multiple=False):
        """Constructor."""
        super().__init__(name)
        self.relation_cls = PIDRelation if not multiple else PIDListRelation
        self.vocabulary_id = vocabulary_id

    @property
    def mapping(self):
        """Return the mapping."""
        _mapping = {
            "type": "object",
            "properties": {
                "@v": {"type": "keyword"},
                "id": {"type": "keyword"},
                "title": {"type": "object", "dynamic": True},
            },
        }

        return _mapping

    def schema(self):
        """Marshmallow schema for vocabulary custom fields."""
        return fields.Mapping()

    def ui_schema(self):
        """Marshmallow UI schema for vocabulary custom fields.

        This schema is used in the UIJSONSerializer and controls how the field will be
        dumped in the UI. It takes responsibility of the localization of strings.
        """
        return fields.Nested(VocabularyL10NItemSchema)

    def options(self):
        """Retrurn the vocabulary options (items)."""
        vocabs = current_service.read_all(
            g.identity, fields=["id", "props", "title", "icon"], type=self.vocabulary_id
        )
        options = []
        for vocab in vocabs:
            options.append(VocabularyL10NItemSchema().dump(vocab))

        return options
