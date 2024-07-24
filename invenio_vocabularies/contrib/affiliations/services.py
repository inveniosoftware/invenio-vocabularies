# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary affiliations."""

from .affiliations import record_type

AffiliationsServiceConfig = record_type.service_config_cls

AffiliationsService = record_type.service_cls
