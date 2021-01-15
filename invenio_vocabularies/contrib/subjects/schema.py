# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Subjects schema."""

from marshmallow import EXCLUDE, INCLUDE, Schema, fields, validate
from marshmallow_utils.fields import Links


class MetadataSchema(Schema):
    """Basic metadata schema class."""

    class Meta:
        """Meta class to accept unknown fields."""

        unknown = INCLUDE

    scheme = fields.Str(required=True, validate=validate.Length(min=3))
    term = fields.Str(required=True, validate=validate.Length(min=3))
    identifier = fields.Str(required=True, validate=validate.Length(min=3))
    title = fields.Str(required=True, validate=validate.Length(min=3))


class SubjectSchema(Schema):
    """Schema for records v1 in JSON."""

    class Meta:
        """Meta class to reject unknown fields."""

        unknown = EXCLUDE

    id = fields.Str()
    metadata = fields.Nested(MetadataSchema)
    created = fields.Str()
    updated = fields.Str()
    links = Links()
    revision_id = fields.Integer(dump_only=True)
