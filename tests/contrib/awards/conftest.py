# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from invenio_indexer.proxies import current_indexer_registry
from invenio_records_resources.proxies import current_service_registry
from sqlalchemy.orm.exc import ObjectDeletedError

from invenio_vocabularies.contrib.awards.api import Award
from invenio_vocabularies.contrib.awards.models import AwardsMetadata
from invenio_vocabularies.contrib.funders.api import Funder
from invenio_vocabularies.contrib.funders.models import FundersMetadata


#
# Funder related fixtures
#
@pytest.fixture(scope="function")
def example_funder(db, identity, funders_service, funder_indexer):
    """Example funder."""
    funder_data = {
        "id": "01ggx4157",
        "name": "CERN",
        "title": {
            "en": "European Organization for Nuclear Research",
            "fr": "Organisation européenne pour la recherche nucléaire",
        },
        "country": "CH",
    }
    funder = funders_service.create(identity, funder_data)
    Funder.index.refresh()  # Refresh the index

    funder_id = funder._record.id
    index = type("index", (), {"_name": funder._record.index._name})
    funder_dict = type(
        "",
        (),
        {
            "index": index(),
            "id": funder._record.id,
            "revision_id": funder._record.revision_id,
        },
    )

    yield funder

    db.session.query(FundersMetadata).filter(FundersMetadata.id == funder_id).delete()

    try:
        funder_indexer.delete(funder._record, refresh=True)
    except ObjectDeletedError:
        funder_indexer.delete(funder_dict(), refresh=True)


@pytest.fixture(scope="function")
def example_funder_ec(db, identity, funders_service, funder_indexer):
    """Example European Commission funder."""
    funder_data = {
        "id": "00k4n6c32",
        "name": "EC",
        "title": {"en": "European Commission", "fr": "Commission Européenne"},
        "country": "BE",
    }
    funder = funders_service.create(identity, funder_data)
    Funder.index.refresh()  # Refresh the index

    funder_id = funder._record.id
    index = type("index", (), {"_name": funder._record.index._name})
    funder_dict = type(
        "",
        (),
        {
            "index": index(),
            "id": funder._record.id,
            "revision_id": funder._record.revision_id,
        },
    )

    yield funder

    db.session.query(FundersMetadata).filter(FundersMetadata.id == funder_id).delete()

    try:
        funder_indexer.delete(funder._record, refresh=True)
    except ObjectDeletedError:
        funder_indexer.delete(funder_dict(), refresh=True)


@pytest.fixture(scope="module")
def funders_service():
    """Funders service object."""
    return current_service_registry.get("funders")


@pytest.fixture()
def funder_indexer():
    """Indexer instance with correct Record class."""
    return current_indexer_registry.get("funders")


#
# Award related fixtures
#
@pytest.fixture(scope="function")
def award_full_data():
    """Full award data."""
    return {
        "id": "755021",
        "identifiers": [
            {
                "identifier": "https://cordis.europa.eu/project/id/755021",
                "scheme": "url",
            }
        ],
        "number": "755021",
        "title": {
            "en": "Personalised Treatment For Cystic Fibrosis Patients With \
                Ultra-rare CFTR Mutations (and beyond)",
        },
        "funder": {"id": "00k4n6c32"},
        "acronym": "HIT-CF",
        "program": "H2020",
    }


@pytest.fixture(scope="function")
def award_full_data_invalid_id():
    """Full award data."""
    return {
        "id": "755021",
        "identifiers": [
            {
                "identifier": "https://cordis.europa.eu/project/id/755021",
                "scheme": "url",
            }
        ],
        "number": "755021",
        "title": {
            "en": "Personalised Treatment For Cystic Fibrosis Patients With \
                Ultra-rare CFTR Mutations (and beyond)",
        },
        "funder": {"id": "010101010"},
        "acronym": "HIT-CF",
        "program": "H2020",
    }


@pytest.fixture(scope="function")
def example_award(db, example_funder_ec, award_full_data, identity, indexer, service):
    """Creates and hard deletes an award."""
    award = service.create(identity, award_full_data)
    Award.index.refresh()  # Refresh the index

    # necessary step for the clean up part after yield
    # award._record could be gone if there was a intended rollback
    # in one of the test functions
    award_id = award._record.id
    index = type("index", (), {"_name": award._record.index._name})
    award_dict = type(
        "",
        (),
        {
            "index": index(),
            "id": award._record.id,
            "revision_id": award._record.revision_id,
        },
    )

    yield award

    # to clean up
    db.session.query(AwardsMetadata).filter(AwardsMetadata.id == award_id).delete()

    try:
        indexer.delete(award._record, refresh=True)
    except ObjectDeletedError:
        indexer.delete(award_dict(), refresh=True)


@pytest.fixture(scope="module")
def service():
    """Awards service object."""
    return current_service_registry.get("awards")


@pytest.fixture()
def indexer():
    """Indexer instance with correct Record class."""
    return current_indexer_registry.get("awards")
