# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Record serializer."""
from functools import partial

from flask_babelex import get_locale
from marshmallow import INCLUDE, Schema, fields


class LocalizedText(fields.Dict):
    """."""

    def _serialize(self, value, attr, obj, **kwargs):
        return value.get(self.locale().language, None)

    def _deserialize(self, value, attr, data, **kwargs):
        raise NotImplementedError  # Unsupported operation

    def __init__(self, locale=None, **kwargs):
        """."""
        fields.Dict.__init__(self, **kwargs)
        self.locale = locale


FormatLocalizedText = partial(LocalizedText, locale=get_locale)


class PresentationVocabularySchema(Schema):
    """Vocabulary presentation."""

    id = fields.Str(attribute="metadata.id")
    type = fields.Str(attribute="vocabulary_type")
    subtype = fields.Str()  # TODO what is this?
    title_l10n = FormatLocalizedText(attribute="metadata.title")
    description_l10n = FormatLocalizedText(attribute="metadata.description")
    icon = fields.Str(attribute="metadata.icon")


class PresentationVocabularyListSchema(Schema):
    """Schema for dumping extra information in the UI."""

    class Meta:
        """."""

        unknown = INCLUDE

    hits = fields.Method('get_hits')
    aggregations = fields.Method('get_aggs')

    def get_hits(self, obj_list):
        """Apply hits transformation."""
        hits = obj_list['hits']['hits']
        for i in range(len(hits)):
            obj = hits[i]
            hits[i] = self.context['object_schema_cls']().dump(obj)
        return obj_list['hits']

    def get_aggs(self, obj_list):
        """Apply aggregations transformation."""
        aggs = obj_list.get("aggregations")
        return aggs
