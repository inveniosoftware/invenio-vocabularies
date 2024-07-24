# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary resource schema."""

from marshmallow import Schema, fields

from invenio_vocabularies.resources.serializer import L10NString


class VocabularyL10Schema(Schema):
    """Vocabulary schema."""

    id = fields.String()
    title = L10NString(data_key="title_l10n")
