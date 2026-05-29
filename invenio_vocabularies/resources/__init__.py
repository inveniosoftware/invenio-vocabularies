# SPDX-FileCopyrightText: 2020-2024 CERN.
# SPDX-License-Identifier: MIT

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
