# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Subjects schema."""

from functools import partial

from invenio_i18n import get_locale
from marshmallow import EXCLUDE, Schema, ValidationError, fields, pre_load, validate
from marshmallow_utils.fields import URL, IdentifierSet, SanitizedUnicode
from marshmallow_utils.schemas import IdentifierSchema

from ...services.schema import (
    BaseVocabularySchema,
    ContribVocabularyRelationSchema,
    i18n_strings,
)
from .config import subject_schemes


class StringOrListOfStrings(fields.Field):
    """Custom field to handle both string and list of strings."""

    # TODO: Move this to marshmallow-utils for broader type support.
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str):
            return fields.String()._deserialize(value, attr, data, **kwargs)
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            return [
                fields.String()._deserialize(item, attr, data, **kwargs)
                for item in value
            ]
        raise ValidationError("Invalid value. Must be a string or a list of strings.")


class SubjectSchema(BaseVocabularySchema):
    """Service schema for subjects."""

    # id in BaseRecordSchema is not required, but I don't see why it shouldn't
    # be, while scheme and subject are required. So I am making it required
    # here.
    id = SanitizedUnicode(required=True)
    scheme = SanitizedUnicode(required=True)
    subject = SanitizedUnicode(required=True)
    title = i18n_strings
    props = fields.Dict(keys=SanitizedUnicode(), values=StringOrListOfStrings())
    identifiers = IdentifierSet(
        fields.Nested(
            partial(
                IdentifierSchema,
                allowed_schemes=subject_schemes,
                identifier_required=False,
            )
        )
    )
    synonyms = fields.List(SanitizedUnicode())

    @pre_load
    def add_subject_from_title(self, data, **kwargs):
        """Add subject from title if not present."""
        locale = get_locale().language
        if "subject" not in data:
            data["subject"] = data["title"].get(locale) or data["title"].values()[0]
        return data


class SubjectRelationSchema(ContribVocabularyRelationSchema):
    """Schema to define an optional subject relation in another schema."""

    # If re-running an OpenAIRE awards update on existing awards which already have subjects,
    # the subject entries will contains `scheme` and `props`, which are unknown since they are `dump_only`.
    # This makes the update exclude unknown field and go through with the update.
    class Meta:
        """Metadata class."""

        unknown = EXCLUDE

    ftf_name = "subject"
    parent_field_name = "subjects"
    subject = SanitizedUnicode()
    scheme = SanitizedUnicode(dump_only=True)
    title = fields.Dict(dump_only=True)
    props = fields.Dict(dump_only=True)
    identifiers = IdentifierSet(
        fields.Nested(
            partial(
                IdentifierSchema,
                allowed_schemes=subject_schemes,
                identifier_required=False,
            )
        )
    )
    synonyms = fields.List(SanitizedUnicode(), dump_only=True)
