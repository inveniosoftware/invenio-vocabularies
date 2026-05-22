# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-License-Identifier: MIT

"""Vocabulary affiliations."""

from .funders import record_type

FundersServiceConfig = record_type.service_config_cls

FundersService = record_type.service_cls
