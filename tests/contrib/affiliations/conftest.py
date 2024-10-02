# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
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
        "acronym": "CERN",
        "id": "01ggx4157",
        "identifiers": [{"identifier": "03yrm5c26", "scheme": "ror"}],
        "name": "Test affiliation",
        "title": {"en": "Test affiliation", "es": "Afiliacion de test"},
        "country": "CH",
        "country_name": "Switzerland",
        "location_name": "Geneva",
        "status": "active",
        "types": ["facility", "funder"],
    }


@pytest.fixture(scope="function")
def affiliation_openaire_data():
    """Full affiliation data."""
    return {
        "acronym": "CERN",
        "id": "01ggx4157",
        "identifiers": [{"identifier": "999988133", "scheme": "pic"}],
        "name": "Test affiliation",
        "title": {"en": "Test affiliation", "es": "Afiliacion de test"},
        "country": "CH",
        "country_name": "Switzerland",
        "location_name": "Geneva",
        "status": "active",
        "types": ["facility", "funder"],
    }


@pytest.fixture(scope="function")
def openaire_affiliation_full_data():
    """Full OpenAIRE affiliation data."""
    return {
        "id": "01ggx4157",
        "identifiers": [{"identifier": "999988133", "scheme": "pic"}],
    }


@pytest.fixture(scope="module")
def service():
    """Affiliations service object."""
    return current_service_registry.get("affiliations")
