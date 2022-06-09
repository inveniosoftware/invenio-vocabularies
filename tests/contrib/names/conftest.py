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

from invenio_vocabularies.contrib.affiliations.api import Affiliation


@pytest.fixture(scope="module")
def service():
    """Names service object."""
    return current_service_registry.get("names")


@pytest.fixture()
def example_affiliation(db):
    """Example affiliation."""
    aff = Affiliation.create(
        {"id": "cern", "name": "European Organization for Nuclear Research"}
    )
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
            {"identifier": "0000-0001-8135-3489", "scheme": "orcid"},
            {"identifier": "gnd:4079154-3", "scheme": "gnd"},
        ],
        "affiliations": [{"id": "cern"}, {"name": "CustomORG"}],
    }
