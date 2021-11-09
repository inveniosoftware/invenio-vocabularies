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
from marshmallow import Schema, ValidationError, fields, post_load, \
    validates_schema
from marshmallow_utils.fields import IdentifierSet, SanitizedUnicode
from marshmallow_utils.schemas import IdentifierSchema

from .config import names_schemes


class AffiliationSchema(Schema):
    """Affiliation of a creator/contributor."""

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
                _("An existing id or a free text name must be present"),
                "names.affiliations"
            )


class NameSchema(BaseRecordSchema):
    """Service schema for names.

    Note that this vocabulary is very different from the base vocabulary
    so it does not inherit from it.
    """

    name = SanitizedUnicode()
    given_name = SanitizedUnicode()
    family_name = SanitizedUnicode()
    identifiers = IdentifierSet(
        fields.Nested(partial(
            IdentifierSchema,
            # It is intended to allow org schemes to be sent as personal
            # and viceversa. This is a trade off learnt from running
            # Zenodo in production.
            allowed_schemes=names_schemes
        ))
    )
    affiliations = fields.List(fields.Nested(AffiliationSchema))

    @validates_schema
    def validate_names(self, data, **kwargs):
        """Validate names."""
        can_compose = data.get('family_name') and data.get("given_name")
        name = data.get("name")
        if not can_compose and not name:
            messages = [
                _("name or family_name and given_name must be present.")
            ]
            raise ValidationError({
                "family_name": messages
            })

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
