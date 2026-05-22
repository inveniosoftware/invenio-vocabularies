# SPDX-FileCopyrightText: 2020-2024 CERN.
# SPDX-FileCopyrightText: 2021 Northwestern University.
# SPDX-License-Identifier: MIT

"""Vocabulary resource schema."""

from marshmallow import Schema, fields

from invenio_vocabularies.resources.serializer import L10NString


class VocabularyL10Schema(Schema):
    """Vocabulary schema."""

    id = fields.String()
    title = L10NString(data_key="title_l10n")
