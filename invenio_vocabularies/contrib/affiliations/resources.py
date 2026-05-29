# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-License-Identifier: MIT

"""Affiliation vocabulary resources."""

from .affiliations import record_type

AffiliationsResourceConfig = record_type.resource_config_cls

AffiliationsResource = record_type.resource_cls
