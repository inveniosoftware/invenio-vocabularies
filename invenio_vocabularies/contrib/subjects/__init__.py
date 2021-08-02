# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Subjects module."""

from .facets import SubjectsLabels
from .resources import SubjectsResource, SubjectsResourceConfig
from .services import SubjectsService, SubjectsServiceConfig

__all__ = [
    "SubjectsLabels",
    "SubjectsResource",
    "SubjectsResourceConfig",
    "SubjectsService",
    "SubjectsServiceConfig",
]
