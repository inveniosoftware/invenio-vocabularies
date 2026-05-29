# SPDX-FileCopyrightText: 2022-2024 CERN.
# SPDX-License-Identifier: MIT

"""Vocabulary awards."""

from .awards import record_type

AwardsServiceConfig = record_type.service_config_cls

AwardsService = record_type.service_cls
