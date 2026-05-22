# SPDX-FileCopyrightText: 2022-2024 CERN.
# SPDX-License-Identifier: MIT

"""Localization serializer for Funders."""

from marshmallow import Schema, fields

from invenio_vocabularies.resources import L10NString


class IdentifierSchema(Schema):
    """Identifier scheme."""

    identifier = fields.String(dump_only=True)
    scheme = fields.String(dump_only=True)


class FunderL10NItemSchema(Schema):
    """Funder serializer schema."""

    id = fields.String(dump_only=True)
    title = L10NString(data_key="title_l10n")
    description = L10NString(data_key="description_l10n")
    props = fields.Dict(dump_only=True)
    name = fields.String(dump_only=True)
    country = fields.String(dump_only=True)
    country_name = fields.String(dump_only=True)
    identifiers = fields.List(fields.Nested(IdentifierSchema), dump_only=True)
