# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabularies configuration."""

import idutils

from .resources.resource import VocabulariesResourceConfig
from .services.service import VocabulariesServiceConfig

VOCABULARIES_RESOURCE_CONFIG = VocabulariesResourceConfig
"""Configure the resource."""

VOCABULARIES_SERVICE_CONFIG = VocabulariesServiceConfig
"""Configure the service."""

VOCABULARIES_AFFILIATION_SCHEMES = {
    "grid": {
        "label": "GRID",
        "validator": lambda x: True
    },
    "gnd": {
        "label": "GND",
        "validator": idutils.is_gnd
    },
    "isni": {
        "label": "ISNI",
        "validator": idutils.is_isni
    },
    "ror": {
        "label": "ROR",
        "validator": idutils.is_ror
    },
}
"""Affiliations allowed identifier schemes."""
