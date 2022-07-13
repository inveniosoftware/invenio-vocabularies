# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Affiliations schema."""

from functools import partial

from flask_babelex import lazy_gettext as _
from marshmallow import fields
from marshmallow_utils.fields import IdentifierSet, SanitizedUnicode
from marshmallow_utils.schemas import IdentifierSchema

from ...services.schema import BaseVocabularySchema, ContribVocabularyRelationSchema
from .config import affiliation_schemes


class AffiliationSchema(BaseVocabularySchema):
    """Service schema for affiliations."""

    acronym = SanitizedUnicode()
    identifiers = IdentifierSet(
        fields.Nested(
            partial(
                IdentifierSchema,
                allowed_schemes=affiliation_schemes,
                identifier_required=False,
            )
        )
    )
    name = SanitizedUnicode(required=True)


class AffiliationRelationSchema(ContribVocabularyRelationSchema):
    """Schema to define an optional affialiation relation in another schema."""

    ftf_name = "name"
    parent_field_name = "affiliations"
    name = SanitizedUnicode()
