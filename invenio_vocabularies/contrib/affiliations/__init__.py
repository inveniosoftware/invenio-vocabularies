# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-FileCopyrightText: 2021 Northwestern University.
# SPDX-License-Identifier: MIT

"""Affiliations module."""

from .resources import AffiliationsResource, AffiliationsResourceConfig
from .services import AffiliationsService, AffiliationsServiceConfig

__all__ = [
    "AffiliationsResource",
    "AffiliationsResourceConfig",
    "AffiliationsService",
    "AffiliationsServiceConfig",
]
