# SPDX-FileCopyrightText: 2022-2024 CERN.
# SPDX-License-Identifier: MIT

"""Custom Fields for InvenioRDM."""

from .subject import SUBJECT_FIELDS, SUBJECT_FIELDS_UI
from .vocabulary import VocabularyCF

__all__ = [
    "VocabularyCF",
    "SUBJECT_FIELDS_UI",
    "SUBJECT_FIELDS",
]
