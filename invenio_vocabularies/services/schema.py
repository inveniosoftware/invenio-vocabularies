# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary service schema."""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.records.schema import BaseRecordSchema
from marshmallow import (
    Schema,
    ValidationError,
    fields,
    post_load,
    pre_dump,
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

    # Nested field type for administration UI form generation
    administration_schema_type = "vocabulary"


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

    # Nested field type for administration UI form generation
    administration_schema_type = "vocabulary"

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
    tags = fields.List(SanitizedUnicode())

    # Nested field type for administration UI form generation
    administration_schema_type = "vocabulary"


class VocabularySchema(BaseVocabularySchema):
    """Service schema for vocabulary records."""

    props = fields.Dict(allow_none=False, keys=fields.Str(), values=fields.Str())
    type = fields.Str(attribute="type.id", required=True)


class ModePIDFieldVocabularyMixin:
    """Mixin for vocabularies using a model field for their PID."""

    @validates_schema
    def validate_id(self, data, **kwargs):
        """Validates ID."""
        is_create = "record" not in self.context
        if is_create and "id" not in data:
            raise ValidationError(_("Missing PID."), "id")
        if not is_create:
            data.pop("id", None)

    @post_load(pass_many=False)
    def move_id(self, data, **kwargs):
        """Moves id to pid."""
        if "id" in data:
            data["pid"] = data.pop("id")
        return data

    @pre_dump(pass_many=False)
    def extract_pid_value(self, data, **kwargs):
        """Extracts the PID value."""
        data["id"] = data.pid.pid_value
        return data


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
