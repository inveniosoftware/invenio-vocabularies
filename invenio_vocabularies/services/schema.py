# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary service schema."""

from invenio_records_resources.services.records.schema import RecordSchema
from marshmallow import EXCLUDE, Schema, fields, validate

i18n_string = fields.Dict(
    allow_none=False,
    keys=fields.Str(validate=validate.Regexp("^[a-z]{2}$")),
    values=fields.Str(),
)


class VocabularyMetadataSchema(Schema):
    """."""

    class Meta:
        """Meta class to reject unknown fields."""

        unknown = EXCLUDE

    title = i18n_string
    description = i18n_string
    icon = fields.Str(allow_none=False)
    props = fields.Dict(
        allow_none=False, keys=fields.Str(), values=fields.Str()
    )


class VocabularySchema(RecordSchema):
    """Schema for records v1 in JSON."""

    class Meta:
        """Meta class to reject unknown fields."""

        unknown = EXCLUDE

    vocabulary_type_id = fields.Integer()
    vocabulary_type = fields.Str()

    metadata = fields.Nested(VocabularyMetadataSchema, required=True)
