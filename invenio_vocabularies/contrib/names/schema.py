# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names schema."""

from functools import partial

from flask_babelex import lazy_gettext as _
from invenio_records_resources.services.records.schema import BaseRecordSchema
from marshmallow import ValidationError, fields, post_load, validates_schema
from marshmallow_utils.fields import IdentifierSet, SanitizedUnicode
from marshmallow_utils.schemas import IdentifierSchema

from ..affiliations.schema import AffiliationRelationSchema
from .config import names_schemes


class NameSchema(BaseRecordSchema):
    """Service schema for names.

    Note that this vocabulary is very different from the base vocabulary
    so it does not inherit from it.
    """

    name = SanitizedUnicode()
    given_name = SanitizedUnicode()
    family_name = SanitizedUnicode()
    identifiers = IdentifierSet(
        fields.Nested(
            partial(
                IdentifierSchema,
                # It is intended to allow org schemes to be sent as personal
                # and viceversa. This is a trade off learnt from running
                # Zenodo in production.
                allowed_schemes=names_schemes,
            )
        )
    )
    affiliations = fields.List(fields.Nested(AffiliationRelationSchema))

    @validates_schema
    def validate_names(self, data, **kwargs):
        """Validate names."""
        can_compose = data.get("family_name") and data.get("given_name")
        name = data.get("name")
        if not can_compose and not name:
            messages = [
                _(
                    "A name or the family name together with the given name must be present."
                )
            ]
            raise ValidationError({"family_name": messages})

    @post_load
    def calculate_name(self, data, **kwargs):
        """Update names for person.

        Fill name from given_name and family_name if person.
        """
        family_name = data.get("family_name")
        given_name = data.get("given_name")
        if family_name and given_name:
            data["name"] = f"{family_name}, {given_name}"

        return data
