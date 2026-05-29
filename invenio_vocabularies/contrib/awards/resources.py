# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-License-Identifier: MIT

"""Award vocabulary resources."""

from .awards import record_type

AwardsResourceConfig = record_type.resource_config_cls

AwardsResource = record_type.resource_cls
