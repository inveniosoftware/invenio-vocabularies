# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-License-Identifier: MIT

"""Funder vocabulary resources."""

from .funders import record_type

FundersResourceConfig = record_type.resource_config_cls

FundersResource = record_type.resource_cls
