# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom Fields for InvenioRDM."""

from invenio_records_resources.records.systemfields import PIDListRelation, PIDRelation
from invenio_records_resources.services.custom_fields.base import BaseCF
from marshmallow import fields

from ...proxies import current_service
from ...records.api import Vocabulary
from ...resources.serializer import VocabularyL10NItemSchema
from ...services.schema import VocabularyRelationSchema


class VocabularyCF(BaseCF):
    """Vocabulary custom field.

    Supporting common vocabulary structure.
    """

    field_keys = ["id", "props", "title", "icon"]
    """Return field's keys for querying.

    These keys are used to select which information to return from the
    vocabulary that is queried.
    """

    def __init__(
        self,
        name,
        vocabulary_id,
        multiple=False,
        dump_options=True,
        sort_by=None,
        schema=VocabularyRelationSchema,
        ui_schema=VocabularyL10NItemSchema,
        **kwargs,
    ):
        """Constructor."""
        super().__init__(name, **kwargs)
        self.relation_cls = PIDRelation if not multiple else PIDListRelation
        self.vocabulary_id = vocabulary_id
        self.dump_options = dump_options
        self.multiple = multiple
        self.sort_by = sort_by
        self.schema = schema
        self.ui_schema = ui_schema
        self.pid_field = Vocabulary.pid.with_type_ctx(self.vocabulary_id)

    @property
    def mapping(self):
        """Return the mapping."""
        _mapping = {
            "type": "object",
            "properties": {
                "@v": {"type": "keyword"},
                "id": {"type": "keyword"},
                "title": {"type": "object", "dynamic": "true"},
            },
        }

        return _mapping

    @property
    def field(self):
        """Marshmallow schema for vocabulary custom fields."""
        return fields.Nested(self.schema, many=self.multiple, **self._field_args)

    @property
    def ui_field(self):
        """Marshmallow UI schema for vocabulary custom fields.

        This schema is used in the UIJSONSerializer and controls how the field will be
        dumped in the UI. It takes responsibility of the localization of strings.
        """
        return fields.Nested(self.ui_schema, many=self.multiple, **self._field_args)

    def options(self, identity):
        """Return UI serialized vocabulary items."""
        if self.dump_options:
            vocabs = current_service.read_all(
                identity,
                fields=self.field_keys,
                type=self.vocabulary_id,
                sort=self.sort_by,
            )
            options = []
            for vocab in vocabs:
                options.append(VocabularyL10NItemSchema().dump(vocab))

            return options
