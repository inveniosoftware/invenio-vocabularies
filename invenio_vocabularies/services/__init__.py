# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Services module."""

from .service import VocabulariesService, VocabulariesServiceConfig

__all__ = (
    "VocabulariesService",
    "VocabulariesServiceConfig",
)
