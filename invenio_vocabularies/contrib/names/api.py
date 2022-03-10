# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary names."""

from ...records.systemfields import ModelPIDField
from .names import record_type


class Name(record_type.record_cls):
    """Name API class."""

    pid = ModelPIDField()
