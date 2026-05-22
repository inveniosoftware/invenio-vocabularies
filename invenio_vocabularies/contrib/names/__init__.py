# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-License-Identifier: MIT

"""Names module."""

from .resources import NamesResource, NamesResourceConfig
from .services import NamesService, NamesServiceConfig

__all__ = (
    "NamesResource",
    "NamesResourceConfig",
    "NamesService",
    "NamesServiceConfig",
)
