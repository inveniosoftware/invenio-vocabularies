# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Affiliations schema."""

from functools import partial

from flask_babelex import lazy_gettext as _
from marshmallow import Schema, ValidationError, fields, validates_schema
from marshmallow_utils.fields import IdentifierSet, SanitizedUnicode
from marshmallow_utils.schemas import IdentifierSchema

from ...services.schema import BaseVocabularySchema
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


class AffiliationRelationSchema(Schema):
    """Schema to define an optional affialiation relation in another schema."""

    id = SanitizedUnicode()
    name = SanitizedUnicode()

    @validates_schema
    def validate_affiliation(self, data, **kwargs):
        """Validates that either id either name are present."""
        id_ = data.get("id")
        name = data.get("name")
        if id_:
            data = {"id": id_}
        elif name:
            data = {"name": name}

        if not id_ and not name:
            raise ValidationError(
                _("An existing id or a free text name must be present."), "affiliations"
            )
