# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom Fields for InvenioRDM."""

from .subject import SUBJECT_FIELDS, SUBJECT_FIELDS_UI
from .vocabulary import VocabularyCF

__all__ = [
    "VocabularyCF",
    "SUBJECT_FIELDS_UI",
    "SUBJECT_FIELDS",
]
