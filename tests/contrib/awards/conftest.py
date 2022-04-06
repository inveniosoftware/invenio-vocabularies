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
from flask_babelex import lazy_gettext as _
from invenio_indexer.api import RecordIndexer
from invenio_records_resources.services.records.facets import TermsFacet

from invenio_vocabularies.contrib.awards.api import Award
from invenio_vocabularies.contrib.awards.config import AwardsSearchOptions
from invenio_vocabularies.contrib.awards.resources import AwardsResource, \
    AwardsResourceConfig
from invenio_vocabularies.contrib.awards.services import AwardsService, \
    AwardsServiceConfig
from invenio_vocabularies.contrib.funders.api import Funder
from invenio_vocabularies.contrib.funders.facets import FundersLabels
from invenio_vocabularies.contrib.funders.resources import FundersResource, \
    FundersResourceConfig
from invenio_vocabularies.contrib.funders.services import FundersService, \
    FundersServiceConfig


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    return {
        "invenio_db.models": [
            "awards = invenio_vocabularies.contrib.awards.models",
            "funders = invenio_vocabularies.contrib.funders.models",
        ],
        "invenio_jsonschemas.schemas": [
            "awards = invenio_vocabularies.contrib.awards.jsonschemas",
            "funders = invenio_vocabularies.contrib.funders.jsonschemas"
        ],
        "invenio_search.mappings": [
            "awards = invenio_vocabularies.contrib.awards.mappings",
            "funders = invenio_vocabularies.contrib.funders.mappings",
        ]
    }


#
# Funder related fixtures
#
@pytest.fixture(scope="function")
def example_funder(db, identity, funders_service, funder_indexer):
    """Example funder."""
    funder_data = {
        "pid": "01ggx4157",
        "name": "CERN",
        "title": {
            "en": "European Organization for Nuclear Research",
            "fr": "Organisation européenne pour la recherche nucléaire"
        },
        "country": "CH"
    }
    fun = funders_service.create(identity, funder_data)
    Funder.index.refresh()  # Refresh the index
    yield fun
    fun._record.delete(force=True)
    funder_indexer.delete(fun._record, refresh=True)
    db.session.commit()


@pytest.fixture()
def funder_indexer():
    """Indexer instance with correct Record class."""
    return RecordIndexer(
        record_cls=Funder,
        record_to_index=lambda r: (r.__class__.index._name, "_doc"),
    )


@pytest.fixture(scope='module')
def funders_service():
    """Funders service object."""
    return FundersService(config=FundersServiceConfig)


@pytest.fixture(scope="module")
def funders_resource(service):
    """Funders resource object."""
    return FundersResource(FundersResourceConfig, service)


#
# Award related fixtures
#
@pytest.fixture(scope="function")
def award_full_data():
    """Full award data."""
    return {
        "pid": "755021",
        "identifiers": [
            {
                "identifier": "https://cordis.europa.eu/project/id/755021",
                "scheme": "url"
            }
        ],
        "number": "755021",
        "title": {
            "en": "Personalised Treatment For Cystic Fibrosis Patients With \
                Ultra-rare CFTR Mutations (and beyond)",
        },
        "funder": {
            "id": "01ggx4157"
        },
        "acronym": "HIT-CF",

    }


@pytest.fixture(scope="function")
def example_award(
    db, example_funder, award_full_data, identity, indexer, service
):
    """Creates and hard deletes an award."""
    award = service.create(identity, award_full_data)
    Award.index.refresh()  # Refresh the index
    yield award
    award._record.delete(force=True)
    indexer.delete(award._record, refresh=True)
    db.session.commit()


@pytest.fixture()
def indexer():
    """Indexer instance with correct Record class."""
    return RecordIndexer(
        record_cls=Award,
        record_to_index=lambda r: (r.__class__.index._name, "_doc"),
    )


@pytest.fixture(scope='module')
def service():
    """Awards service object."""
    class MockAwardsSearchOptions(AwardsSearchOptions):
        """Mock search options to add funders facet."""

        facets = {
            'funders': TermsFacet(
                field='funder.id',
                label=_('Funders'),
                value_labels=FundersLabels('funders')
            )
        }

    class MockAwardsServiceConfig(AwardsServiceConfig):
        """Mock resource config to add funders facet."""

        search = MockAwardsSearchOptions

    return AwardsService(config=MockAwardsServiceConfig)


@pytest.fixture(scope="module")
def resource(service):
    """Awards resource object."""
    return AwardsResource(AwardsResourceConfig, service)


@pytest.fixture(scope="module")
def base_app(base_app, resource, service, funders_resource, funders_service):
    """Application factory fixture.

    Registers awards' resource and service.
    """
    base_app.register_blueprint(funders_resource.as_blueprint())
    base_app.register_blueprint(resource.as_blueprint())
    registry = base_app.extensions['invenio-records-resources'].registry
    registry.register(funders_service, service_id='funders')
    registry.register(service, service_id='awards')
    yield base_app
