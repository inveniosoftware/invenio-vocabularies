# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""System fields module."""

from .pid import BaseVocabularyPIDFieldContext, VocabularyPIDFieldContext

__all__ = (
    'BaseVocabularyPIDFieldContext',
    'VocabularyPIDFieldContext',
)
