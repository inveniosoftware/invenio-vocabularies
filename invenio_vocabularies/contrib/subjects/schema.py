# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021-2022 CERN.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Subjects schema."""

from functools import partial

from invenio_i18n import lazy_gettext as _
from marshmallow import fields
from marshmallow_utils.fields import IdentifierSet, SanitizedUnicode
from marshmallow_utils.schemas import IdentifierSchema

from ...services.schema import (
    BaseVocabularySchema,
    ContribVocabularyRelationSchema,
    i18n_strings,
)
from .config import subject_schemes


class SubjectSchema(BaseVocabularySchema):
    """Service schema for subjects."""

    # id in BaseRecordSchema is not required, but I don't see why it shouldn't
    # be, while scheme and subject are required. So I am making it required
    # here.
    id = SanitizedUnicode(required=True)
    scheme = SanitizedUnicode(required=True)
    subject = SanitizedUnicode(required=True)
    title = i18n_strings
    synonyms = fields.List(SanitizedUnicode())


class SubjectRelationSchema(ContribVocabularyRelationSchema):
    """Schema to define an optional subject relation in another schema."""

    ftf_name = "subject"
    parent_field_name = "subjects"
    subject = SanitizedUnicode()
    scheme = SanitizedUnicode()
    title = i18n_strings
    synonyms = fields.List(SanitizedUnicode())
