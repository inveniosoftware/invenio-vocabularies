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
from marshmallow import Schema, ValidationError, fields, post_load, pre_dump, \
    pre_load, validate, validates_schema
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

    pid = SanitizedUnicode(required=True)
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

    # TODO: the 3 hooks below could be extracted to a PIDField
    @pre_load(pass_many=False)
    def load_pid(self, data, **kwargs):
        """Loads the pid.

        If it does not exist, it tries to extract it from the identifiers.
        """
        if data.get("pid"):
            return data

        identifiers = data.get("identifiers", [])
        for identifier in identifiers:
            # FIXME: make scheme configurable
            if identifier["scheme"] == "ror":
                data["pid"] = identifier["identifier"]
                break

        return data

    @post_load
    def kepp_pid_on_create(self, data, **kwargs):
        """Remove the PID if already registered.

        If the pid is not removed it would be injected into the DB JSON column.
        Since the field is only popped on_create by PIDComponent.
        """
        if self.context.get("pid"):
            data.pop("pid")

        return data

    @pre_dump(pass_many=False)
    def extract_pid_value(self, data, **kwargs):
        """Extracts the PID value."""
        if not data.get('pid'):
            data['pid'] = data.pid.pid_value

        return data
