# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary awards."""

from .awards import record_type

AwardsServiceConfig = record_type.service_config_cls

AwardsService = record_type.service_cls
