# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Funders schema."""

from functools import partial

from flask_babelex import lazy_gettext as _
from marshmallow import Schema, ValidationError, fields, validate, \
    validates_schema
from marshmallow_utils.fields import IdentifierSet, SanitizedUnicode
from marshmallow_utils.schemas import IdentifierSchema

from ...services.schema import BaseVocabularySchema
from .config import funder_schemes


class FunderRelationSchema(Schema):
    """Funder schema."""

    name = SanitizedUnicode(
        validate=validate.Length(min=1, error=_('Name cannot be blank.'))
    )
    id = SanitizedUnicode()

    @validates_schema
    def validate_funder(self, data, **kwargs):
        """Validates that either id either name are present."""
        id_ = data.get("id")
        name = data.get("name")
        if id_:
            data = {"id": id_}
        elif name:
            data = {"name": name}

        if not id_ and not name:
            raise ValidationError(
                _("An existing id or a free text name must be present"),
                "affiliations"
            )


class FunderSchema(BaseVocabularySchema):
    """Service schema for funders."""

    name = SanitizedUnicode(
        required=True,
        validate=validate.Length(min=1, error=_('Name cannot be blank.'))
    )
    country = SanitizedUnicode()
    identifiers = IdentifierSet(fields.Nested(
        partial(
            IdentifierSchema,
            allowed_schemes=funder_schemes,
            identifier_required=False
        )
    ))
