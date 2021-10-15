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

from invenio_vocabularies.contrib.affiliations.api import Affiliation
from invenio_vocabularies.contrib.names.services import NamesService, \
    NamesServiceConfig


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    # affiliations are needed due to sysfield relation
    return {
        "invenio_db.models": [
            "affiliations = invenio_vocabularies.contrib.affiliations.models",
            "names = invenio_vocabularies.contrib.names.models",
        ],
        "invenio_jsonschemas.schemas": [
            "affiliations = \
                invenio_vocabularies.contrib.affiliations.jsonschemas",
            "names = invenio_vocabularies.contrib.names.jsonschemas",
        ],
        "invenio_search.mappings": [
            "names = \
                invenio_vocabularies.contrib.names.mappings",
        ]
    }


@pytest.fixture(scope='module')
def service():
    """Names service object."""
    return NamesService(config=NamesServiceConfig)


@pytest.fixture()
def example_affiliation(db):
    """Example affiliation."""
    aff = Affiliation.create({"id": "cern"})
    Affiliation.pid.create(aff)
    aff.commit()
    db.session.commit()
    return aff


@pytest.fixture(scope="function")
def name_full_data():
    """Full name data."""
    return {
        "name": "Doe, John",
        "given_name": "John",
        "family_name": "Doe",
        "identifiers": [
            {
                "identifier": "0000-0001-8135-3489",
                "scheme": "orcid"
            }
        ],
        "affiliations": [
            {
                "id": "cern"
            },
            {
                "name": "CustomORG"
            }
        ]
    }
