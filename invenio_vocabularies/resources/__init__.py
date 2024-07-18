# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Resources module."""

from invenio_vocabularies.resources.schema import L10NString, VocabularyL10Schema

from .config import VocabulariesResourceConfig, VocabularyTypeResourceConfig
from .resource import VocabulariesAdminResource, VocabulariesResource

__all__ = (
    "VocabularyL10Schema",
    "L10NString",
    "VocabulariesResourceConfig",
    "VocabularyTypeResourceConfig",
    "VocabulariesAdminResource",
    "VocabulariesResource",
)
