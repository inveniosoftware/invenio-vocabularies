# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom Fields for InvenioRDM."""

from flask import g
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
        # FIXME: can objects be done with ES objects
        # deal with compatibility between versions (e.g. keyword changes name)
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
        # FIXME: use common schema
        # https://github.com/inveniosoftware/invenio-vocabularies/issues/188
        # This need to `UNKONW=EXCLUDE`
        return fields.Mapping()

    def options(self):
        """Retrurn the vocabulary options (items)."""
        # FIXME: should use g.identity? or be pass identity as argument?
        # I prefer the second
        vocabs = current_service.read_all(
            g.identity,
            fields=["id", "props", "title", "icon"],
            type=self.vocabulary_id
        )

        options = []

        for vocab in vocabs:
            # FIXME: should return properly title, id, props icon
            # should serialize in ui (app-rdm/react)
            options.append(
                {
                    "value": vocab["id"],
                    "text": vocab["title"]["en"],
                    # "icon": vocab["icon"],
                    # "props": vocab["props"],
                }
            )

        return options
