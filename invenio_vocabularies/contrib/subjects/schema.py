# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Subjects schema."""

from marshmallow import fields
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
