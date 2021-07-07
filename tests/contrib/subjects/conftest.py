# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest

from invenio_vocabularies.contrib.subjects.resources import SubjectsResource, \
    SubjectsResourceConfig
from invenio_vocabularies.contrib.subjects.services import SubjectsService, \
    SubjectsServiceConfig


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    return {
        "invenio_db.models": [
            "subjects = invenio_vocabularies.contrib.subjects.models",
        ],
        "invenio_jsonschemas.schemas": [
            "subjects = invenio_vocabularies.contrib.subjects.jsonschemas",
        ],
        "invenio_search.mappings": [
            "subjects = invenio_vocabularies.contrib.subjects.mappings",
        ]
    }


@pytest.fixture(scope="function")
def subject_full_data():
    """Controlled vocabulary backed subject data."""
    return {
        "id": "https://id.nlm.nih.gov/mesh/D000001",
        "scheme": "MeSH",
        "subject": "Calcimycin"
    }


@pytest.fixture(scope='module')
def service():
    """Subjects service object."""
    return SubjectsService(config=SubjectsServiceConfig)


@pytest.fixture(scope="module")
def resource(service):
    """Subjects resource object."""
    return SubjectsResource(SubjectsResourceConfig, service)


@pytest.fixture(scope="module")
def base_app(base_app, resource, service):
    """Application factory fixture.

    Registers subjects' resource and service.
    """
    base_app.register_blueprint(resource.as_blueprint())
    registry = base_app.extensions['invenio-records-resources'].registry
    registry.register(service, service_id='subjects-service')
    yield base_app
