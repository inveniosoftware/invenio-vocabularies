# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names services."""

from .names import record_type

NamesServiceConfig = record_type.service_config_cls

NamesService = record_type.service_cls
