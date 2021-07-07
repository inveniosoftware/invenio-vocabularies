# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the affiliation vocabulary resources."""

from .subjects import record_type

SubjectsResourceConfig = record_type.resource_config_cls
SubjectsResourceConfig.routes["item"] = "/<path:pid_value>"

SubjectsResource = record_type.resource_cls
