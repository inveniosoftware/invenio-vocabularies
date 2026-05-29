# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-License-Identifier: MIT

"""Funders vocabulary."""

from .resources import FundersResource, FundersResourceConfig
from .services import FundersService, FundersServiceConfig

__all__ = [
    "FundersResource",
    "FundersResourceConfig",
    "FundersService",
    "FundersServiceConfig",
]
