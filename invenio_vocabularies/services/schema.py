# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary service schema."""

from invenio_records_resources.services.records.schema import BaseRecordSchema
from marshmallow import EXCLUDE, RAISE, Schema, fields, validate
from marshmallow_utils.fields import SanitizedUnicode

i18n_strings = fields.Dict(
    allow_none=False,
    keys=fields.Str(validate=validate.Regexp("^[a-z]{2}$")),
    values=fields.Str(),
)
"""Field definition for language aware strings."""


class BaseVocabularySchema(BaseRecordSchema):
    """Base schema for vocabularies."""

    title = i18n_strings
    description = i18n_strings
    icon = fields.Str(allow_none=False)


class VocabularySchema(BaseVocabularySchema):
    """Service schema for vocabulary records.."""

    tags = fields.List(SanitizedUnicode())
    type = fields.Str(attribute='type.id', required=True)
    props = fields.Dict(
        allow_none=False, keys=fields.Str(), values=fields.Str()
    )
