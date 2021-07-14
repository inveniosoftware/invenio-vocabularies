# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Affiliations module."""

from .resources import AffiliationsResource, AffiliationsResourceConfig
from .services import AffiliationsService, AffiliationsServiceConfig

__all__ = [
    "AffiliationsResource",
    "AffiliationsResourceConfig",
    "AffiliationsService",
    "AffiliationsServiceConfig",
]
