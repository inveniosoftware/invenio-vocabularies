# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Awards vocabulary."""

from .resources import AwardsResource, AwardsResourceConfig
from .services import AwardsService, AwardsServiceConfig

__all__ = [
    "AwardsResource",
    "AwardsResourceConfig",
    "AwardsService",
    "AwardsServiceConfig",
]
