# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary service schema."""

from flask_babelex import lazy_gettext as _
from invenio_records_resources.services.records.schema import BaseRecordSchema
from marshmallow import (
    Schema,
    ValidationError,
    fields,
    pre_load,
    validate,
    validates_schema,
)
from marshmallow_utils.fields import SanitizedUnicode

i18n_strings = fields.Dict(
    allow_none=False,
    keys=fields.Str(validate=validate.Regexp("^[a-z]{2}$")),
    values=fields.Str(),
)
"""Field definition for language aware strings."""


class BaseVocabularyRelationSchema(Schema):
    """Base Vocabulary relation schema."""

    id = SanitizedUnicode(required=True)


class VocabularyRelationSchema(BaseVocabularyRelationSchema):
    """Vocabulary relation schema."""

    title = fields.Dict(dump_only=True)

    @pre_load
    def clean(self, data, **kwargs):
        """Removes dump_only fields.

        Why: We want to allow the output of a Schema dump, to be a valid input
             to a Schema load without causing strange issues.
        """
        value_is_dict = isinstance(data, dict)
        if value_is_dict:
            for name, field in self.fields.items():
                if field.dump_only:
                    data.pop(name, None)
        return data


class ContribVocabularyRelationSchema(Schema):
    """Base Vocabulary relation schema."""

    id = SanitizedUnicode()
    ftf_name = None  # free text field name
    parent_field_name = None

    @validates_schema
    def validate_relation_schema(self, data, **kwargs):
        """Validates that either id either the free text field are present."""
        id_ = data.get("id")
        free_text = data.get(self.ftf_name)
        if id_:
            data = {"id": id_}
        elif free_text:
            data = {self.ftf_name: free_text}

        if not id_ and not free_text:
            raise ValidationError(
                _(
                    "An existing id or a free text {ftf_name} must be present.".format(
                        ftf_name=self.ftf_name
                    )
                ),
                self.parent_field_name,
            )


class BaseVocabularySchema(BaseRecordSchema):
    """Base schema for vocabularies."""

    title = i18n_strings
    description = i18n_strings
    icon = fields.Str(allow_none=False)


class VocabularySchema(BaseVocabularySchema):
    """Service schema for vocabulary records."""

    props = fields.Dict(allow_none=False, keys=fields.Str(), values=fields.Str())
    tags = fields.List(SanitizedUnicode())
    type = fields.Str(attribute="type.id", required=True)


class DatastreamObject(Schema):
    """Datastream object (reader, transformer, writer)."""

    type = fields.Str(required=True)
    args = fields.Dict(keys=fields.Str(), values=fields.Field)


class TaskSchema(Schema):
    """Service schema for vocabulary tasks."""

    readers = fields.List(
        fields.Nested(DatastreamObject),
        validate=validate.Length(min=1),
        required=True,
    )
    transformers = fields.List(
        fields.Nested(DatastreamObject),
        validate=validate.Length(min=1),
        required=False,
    )
    writers = fields.List(
        fields.Nested(DatastreamObject),
        validate=validate.Length(min=1),
        required=True,
    )
