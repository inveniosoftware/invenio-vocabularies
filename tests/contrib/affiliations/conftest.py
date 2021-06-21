# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest

from invenio_vocabularies.contrib.affiliations.services import \
    AffiliationsService, AffiliationsServiceConfig


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    return {
        "invenio_db.models": [
            "affiliations = invenio_vocabularies.contrib.affiliations.models",
        ],
        "invenio_jsonschemas.schemas": [
            "affiliations = \
                invenio_vocabularies.contrib.affiliations.jsonschemas",
        ],
        "invenio_search.mappings": [
            "affiliations = \
                invenio_vocabularies.contrib.affiliations.mappings",
        ]
    }


@pytest.fixture(scope="function")
def affiliation_full_data():
    """Full affiliation data."""
    return {
        "acronym": "TEST",
        "id": "cern",
        "identifiers": [
            {"identifier": "03yrm5c26", "scheme": "ror"}
        ],
        "name": "Test affiliation",
        "title": {
            "en": "Test affiliation",
            "es": "Afiliacion de test"
        }
    }


@pytest.fixture(scope='module')
def service(app):
    """Vocabularies service object."""
    return AffiliationsService(config=AffiliationsServiceConfig)
