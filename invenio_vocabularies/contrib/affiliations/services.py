# SPDX-FileCopyrightText: 2021-2024 CERN.
# SPDX-License-Identifier: MIT

"""Vocabulary affiliations."""

from .affiliations import record_type

AffiliationsServiceConfig = record_type.service_config_cls

AffiliationsService = record_type.service_cls
