# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Record serializer."""

from functools import partial

import flask_babelex
from marshmallow import INCLUDE, Schema, fields


class LocalizedText(fields.Dict):
    """A localized text field."""

    def _serialize(self, value, attr, obj, **kwargs):
        return value.get(flask_babelex.get_locale().language, None)

    def _deserialize(self, value, attr, data, **kwargs):
        raise NotImplementedError  # Unsupported operation


class PresentationVocabularySchema(Schema):
    """Vocabulary presentation."""

    id = fields.Str(attribute="id")
    type = fields.Str(attribute="vocabulary_type")
    title = LocalizedText(attribute="metadata.title")
    description = LocalizedText(attribute="metadata.description")
    icon = fields.Str(attribute="metadata.icon")


class PresentationVocabularyListSchema(Schema):
    """Schema for dumping extra information in the UI."""

    class Meta:
        """Ignore other fields."""

        unknown = INCLUDE

    hits = fields.Method("get_hits")
    aggregations = fields.Method("get_aggs")

    def get_hits(self, obj_list):
        """Apply hits transformation."""
        hits = obj_list["hits"]["hits"]
        for i in range(len(hits)):
            obj = hits[i]
            hits[i] = self.context["object_schema_cls"]().dump(obj)
        return obj_list["hits"]

    def get_aggs(self, obj_list):
        """Apply aggregations transformation."""
        aggs = obj_list.get("aggregations")
        return aggs
