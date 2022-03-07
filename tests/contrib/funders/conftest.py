# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest

from invenio_vocabularies.contrib.funders.resources import FundersResource, \
    FundersResourceConfig
from invenio_vocabularies.contrib.funders.services import FundersService, \
    FundersServiceConfig


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    return {
        "invenio_db.models": [
            "funders = invenio_vocabularies.contrib.funders.models",
        ],
        "invenio_jsonschemas.schemas": [
            "funders = \
                invenio_vocabularies.contrib.funders.jsonschemas",
        ],
        "invenio_search.mappings": [
            "funders = \
                invenio_vocabularies.contrib.funders.mappings",
        ]
    }


@pytest.fixture(scope="function")
def funder_full_data():
    """Full funder data."""
    return {
        "id": "fund",
        #     pid="01ggx4157",
        "identifiers": [
            {
                "identifier": "000000012156142X",
                "scheme": "isni",
            },
            {
                "identifier": "grid.9132.9",
                "scheme": "grid",
            }
        ],
        "name": "CERN",
        "title": {
            "en": "European Organization for Nuclear Research",
            "fr": "Organisation européenne pour la recherche nucléaire"
        },
        "country": "CH"
    }


@pytest.fixture(scope='module')
def service():
    """Funders service object."""
    return FundersService(config=FundersServiceConfig)


@pytest.fixture(scope="module")
def resource(service):
    """Funders resource object."""
    return FundersResource(FundersResourceConfig, service)


@pytest.fixture(scope="module")
def base_app(base_app, resource, service):
    """Application factory fixture.

    Registers funders' resource and service.
    """
    base_app.register_blueprint(resource.as_blueprint())
    registry = base_app.extensions['invenio-records-resources'].registry
    registry.register(service, service_id='funders-service')
    yield base_app
