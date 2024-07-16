# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Services module."""

from .config import VocabulariesServiceConfig, VocabularyTypesServiceConfig
from .service import VocabulariesService, VocabularyTypeService

__all__ = (
    "VocabulariesService",
    "VocabularyTypeService",
    "VocabulariesServiceConfig",
    "VocabularyTypesServiceConfig",
)
