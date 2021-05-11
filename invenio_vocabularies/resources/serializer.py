# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Localization serializer for Vocabularies."""

from functools import partial

from flask import current_app
from flask_babelex import get_locale
from marshmallow import Schema, fields
from marshmallow_utils.fields import BabelGettextDictField


def current_default_locale():
    """Get the Flask app's default locale."""
    if current_app:
        return current_app.config.get('BABEL_DEFAULT_LOCALE', 'en')
    # Use english by default if not specified
    return 'en'


L10NString = partial(BabelGettextDictField, get_locale, current_default_locale)


class VocabularyL10NItemSchema(Schema):
    """Vocabulary serializer schema."""

    id = fields.String(dump_only=True)
    title = L10NString(data_key='title_l10n')
    description = L10NString(data_key='description_l10n')
    props = fields.Dict(dump_only=True)
    icon = fields.String(dump_only=True)
    tags = fields.List(fields.Str(), dump_only=True)


class VocabularyL10NListSchema(Schema):
    """Vocabulary serializer schema."""

    hits = fields.Method('get_hits')

    def get_hits(self, obj_list):
        """Apply hits transformation."""
        schema = self.context['schema_cls']()
        obj_list['hits']['hits'] = [
            schema.dump(h) for h in obj_list['hits']['hits']
        ]
        return obj_list['hits']
