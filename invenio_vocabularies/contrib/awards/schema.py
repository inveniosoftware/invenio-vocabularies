# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Awards schema."""

from flask_babelex import lazy_gettext as _
from marshmallow import Schema, ValidationError, fields, validate, \
    validates_schema
from marshmallow_utils.fields import SanitizedUnicode

from ..funders.schema import FunderRelationSchema


class AwardRelationSchema(Schema):
    """Award schema."""

    title = SanitizedUnicode(
        required=True,
        validate=validate.Length(min=1, error=_('Title cannot be blank.'))
    )
    number = SanitizedUnicode(
        required=True,
        validate=validate.Length(min=1, error=_('Number cannot be blank.'))
    )
    scheme = SanitizedUnicode()
    identifier = SanitizedUnicode()


class FundingRelationSchema(Schema):
    """Funding schema."""

    funder = fields.Nested(FunderRelationSchema)
    award = fields.Nested(AwardRelationSchema)

    @validates_schema
    def validate_data(self, data, **kwargs):
        """Validate either funder or award is present."""
        funder = data.get('funder')
        award = data.get('award')
        if not funder and not award:
            raise ValidationError(
                {"funding": _("At least award or funder should be present.")})
