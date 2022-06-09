# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from invenio_records_resources.proxies import current_service_registry


@pytest.fixture(scope="function")
def affiliation_full_data():
    """Full affiliation data."""
    return {
        "acronym": "TEST",
        "id": "cern",
        "identifiers": [{"identifier": "03yrm5c26", "scheme": "ror"}],
        "name": "Test affiliation",
        "title": {"en": "Test affiliation", "es": "Afiliacion de test"},
    }


@pytest.fixture(scope="module")
def service():
    """Affiliations service object."""
    return current_service_registry.get("affiliations")
