# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2024 California Institute of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Affiliations schema."""

from functools import partial

from invenio_i18n import lazy_gettext as _
from marshmallow import fields, validate
from marshmallow_utils.fields import IdentifierSet, SanitizedUnicode
from marshmallow_utils.schemas import IdentifierSchema

from ...services.schema import (
    BaseVocabularySchema,
    ContribVocabularyRelationSchema,
    ModePIDFieldVocabularyMixin,
)
from .config import affiliation_schemes


class AffiliationSchema(BaseVocabularySchema, ModePIDFieldVocabularyMixin):
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
    name = SanitizedUnicode(
        required=True, validate=validate.Length(min=1, error=_("Name cannot be blank."))
    )
    country = SanitizedUnicode()
    country_name = SanitizedUnicode()
    location_name = SanitizedUnicode()
    id = SanitizedUnicode(
        validate=validate.Length(min=1, error=_("PID cannot be blank."))
    )

    acronym = SanitizedUnicode()
    aliases = fields.List(SanitizedUnicode())
    status = SanitizedUnicode()
    types = fields.List(SanitizedUnicode())


class AffiliationRelationSchema(ContribVocabularyRelationSchema):
    """Schema to define an optional affialiation relation in another schema."""

    ftf_name = "name"
    parent_field_name = "affiliations"
    name = SanitizedUnicode()
    identifiers = IdentifierSet(
        fields.Nested(
            partial(
                IdentifierSchema,
                allowed_schemes=affiliation_schemes,
                identifier_required=False,
            )
        ),
        dump_only=True,
    )
