# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-FileCopyrightText: 2021 Northwestern University.
# SPDX-License-Identifier: MIT

"""Test the affiliation vocabulary resources."""

from .subjects import record_type

SubjectsResourceConfig = record_type.resource_config_cls
SubjectsResourceConfig.routes["item"] = "/<path:pid_value>"

SubjectsResource = record_type.resource_cls
