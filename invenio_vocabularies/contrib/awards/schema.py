# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Awards schema."""

from functools import partial

from attr import attr
from flask_babelex import lazy_gettext as _
from marshmallow import (
    Schema,
    ValidationError,
    fields,
    post_load,
    pre_dump,
    validate,
    validates_schema,
)
from marshmallow_utils.fields import IdentifierSet, SanitizedUnicode
from marshmallow_utils.schemas import IdentifierSchema

from ...services.schema import BaseVocabularySchema, i18n_strings
from ..funders.schema import FunderRelationSchema
from .config import award_schemes


class AwardSchema(BaseVocabularySchema):
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

    id = SanitizedUnicode(
        validate=validate.Length(min=1, error=_("Pid cannot be blank."))
    )

    @validates_schema
    def validate_id(self, data, **kwargs):
        """Validates ID."""
        is_create = "record" not in self.context
        if is_create and "id" not in data:
            raise ValidationError(_("Missing PID."), "id")
        if not is_create:
            data.pop("id", None)

    @post_load(pass_many=False)
    def move_id(self, data, **kwargs):
        """Moves id to pid."""
        if "id" in data:
            data["pid"] = data.pop("id")
        return data

    @pre_dump(pass_many=False)
    def extract_pid_value(self, data, **kwargs):
        """Extracts the PID value."""
        data["id"] = data.pid.pid_value
        return data


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

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate either id or number/title are present."""
        id_ = data.get("id")
        number = data.get("number")
        title = data.get("title")
        if not id_ and not (number and title):
            raise ValidationError(
                _("An existing id or number/title must be present."), "award"
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
