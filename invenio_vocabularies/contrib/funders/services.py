# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary affiliations."""

from .funders import record_type

FundersServiceConfig = record_type.service_config_cls

FundersService = record_type.service_cls
