# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Awards schema."""

from functools import partial

from invenio_i18n import lazy_gettext as _
from marshmallow import Schema, ValidationError, fields, validate, validates_schema
from marshmallow_utils.fields import IdentifierSet, ISODateString, SanitizedUnicode
from marshmallow_utils.schemas import IdentifierSchema

from ...services.schema import (
    BaseVocabularySchema,
    ContribVocabularyRelationSchema,
    ModePIDFieldVocabularyMixin,
    i18n_strings,
)
from ..funders.schema import FunderRelationSchema
from ..subjects.schema import SubjectRelationSchema
from .config import award_schemes


class AwardOrganizationRelationSchema(ContribVocabularyRelationSchema):
    """Schema to define an organization relation in an award."""

    ftf_name = "organization"
    parent_field_name = "organizations"
    organization = SanitizedUnicode()
    scheme = SanitizedUnicode()


class AwardSchema(BaseVocabularySchema, ModePIDFieldVocabularyMixin):
    """Award schema."""

    identifiers = IdentifierSet(
        fields.Nested(
            partial(
                IdentifierSchema,
                allowed_schemes=award_schemes,
                identifier_required=False,
            )
        )
    )
    number = SanitizedUnicode(
        required=True,
        validate=validate.Length(min=1, error=_("Number cannot be blank.")),
    )
    funder = fields.Nested(FunderRelationSchema)

    acronym = SanitizedUnicode()

    program = SanitizedUnicode()

    subjects = fields.List(fields.Nested(SubjectRelationSchema))

    organizations = fields.List(fields.Nested(AwardOrganizationRelationSchema))

    start_date = ISODateString()

    end_date = ISODateString()

    id = SanitizedUnicode(
        validate=validate.Length(min=1, error=_("PID cannot be blank."))
    )


class AwardRelationSchema(Schema):
    """Award relation schema."""

    id = SanitizedUnicode()
    number = SanitizedUnicode()
    title = i18n_strings
    identifiers = IdentifierSet(
        fields.Nested(
            partial(
                IdentifierSchema,
                allowed_schemes=award_schemes,
                identifier_required=False,
            )
        )
    )
    acronym = SanitizedUnicode()
    program = SanitizedUnicode()

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate either id or number/title are present."""
        id_ = data.get("id")
        number = data.get("number")
        title = data.get("title")

        if not id_ and not (number or title):
            raise ValidationError(
                _("An existing id or either number or title must be present."),
                "award",
            )


class FundingRelationSchema(Schema):
    """Funding schema."""

    funder = fields.Nested(FunderRelationSchema)
    award = fields.Nested(AwardRelationSchema)

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate either funder or award is present."""
        funder = data.get("funder")
        award = data.get("award")
        if not funder and not award:
            raise ValidationError(
                {"funding": _("At least award or funder should be present.")}
            )
