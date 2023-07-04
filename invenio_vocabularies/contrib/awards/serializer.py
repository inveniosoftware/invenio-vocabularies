# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Localization serializer for Awards."""

from marshmallow import Schema, fields

from invenio_vocabularies.resources import L10NString


class IdentifierSchema(Schema):
    """Identifier scheme."""

    identifier = fields.String(dump_only=True)
    scheme = fields.String(dump_only=True)


class FunderRelationSchema(Schema):
    """Funder schema."""

    name = fields.String(dump_only=True)
    id = fields.String(dump_only=True)


class AwardL10NItemSchema(Schema):
    """Award serializer schema."""

    id = fields.String(dump_only=True)
    title = L10NString(data_key="title_l10n")
    description = L10NString(data_key="description_l10n")
    number = fields.String(dump_only=True)
    acronym = fields.String(dump_only=True)
    funder = fields.Nested(FunderRelationSchema, dump_only=True)
    identifiers = fields.List(fields.Nested(IdentifierSchema), dump_only=True)
