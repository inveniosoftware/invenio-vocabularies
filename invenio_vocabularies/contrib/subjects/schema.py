# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Subjects schema."""

from flask_babelex import lazy_gettext as _
from marshmallow import Schema, ValidationError, validates_schema
from marshmallow_utils.fields import SanitizedUnicode

from ...services.schema import BaseVocabularySchema


class SubjectSchema(BaseVocabularySchema):
    """Service schema for subjects."""

    # id in BaseRecordSchema is not required, but I don't see why it shouldn't
    # be, while scheme and subject are required. So I am making it required
    # here.
    id = SanitizedUnicode(required=True)
    scheme = SanitizedUnicode(required=True)
    subject = SanitizedUnicode(required=True)


class SubjectRelationSchema(Schema):
    """Schema to define an optional subject relation in another schema."""

    id = SanitizedUnicode()
    subject = SanitizedUnicode()
    scheme = SanitizedUnicode()

    @validates_schema
    def validate_subject(self, data, **kwargs):
        """Validates that either id either name are present."""
        id_ = data.get("id")
        subject = data.get("subject")
        if id_:
            data = {"id": id_}
        elif subject:
            data = {"subject": subject}

        if not id_ and not subject:
            raise ValidationError(
                _("An existing id or a free text subject must be present."), "subjects"
            )
