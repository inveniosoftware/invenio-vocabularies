# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names vocabulary resources."""

from .names import record_type

NamesResourceConfig = record_type.resource_config_cls

NamesResource = record_type.resource_cls
