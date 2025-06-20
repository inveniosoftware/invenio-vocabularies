# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names module."""

from .resources import NamesResource, NamesResourceConfig
from .services import NamesService, NamesServiceConfig

__all__ = (
    "NamesResource",
    "NamesResourceConfig",
    "NamesService",
    "NamesServiceConfig",
)
