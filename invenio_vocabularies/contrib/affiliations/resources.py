# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Affiliation vocabulary resources."""

from .affiliations import record_type

AffiliationsResourceConfig = record_type.resource_config_cls

AffiliationsResource = record_type.resource_cls
