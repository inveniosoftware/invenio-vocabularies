# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Affiliations schema."""

from invenio_records_resources.services.records.schema import BaseRecordSchema
from marshmallow import EXCLUDE, RAISE, Schema, fields, validate
from marshmallow_utils.fields import IdentifierSet, SanitizedUnicode
from marshmallow_utils.schemas import IdentifierSchema

from ...services.schema import BaseVocabularySchema


class AffiliationSchema(BaseVocabularySchema):
    """Service schema for affiliations."""

    acronym = SanitizedUnicode()
    identifiers = IdentifierSet(fields.Nested(IdentifierSchema))
    name = SanitizedUnicode(required=True)
