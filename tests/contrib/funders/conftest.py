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
from invenio_db import db
from invenio_indexer.proxies import current_indexer_registry
from invenio_records_resources.proxies import current_service_registry
from sqlalchemy.orm.exc import ObjectDeletedError

from invenio_vocabularies.contrib.funders.api import Funder
from invenio_vocabularies.contrib.funders.models import FundersMetadata


@pytest.fixture(scope="function")
def funder_full_data():
    """Full funder data."""
    return {
        "id": "01ggx4157",
        "identifiers": [
            {"scheme": "ror", "identifier": "01ggx4157"},
            {
                "identifier": "0000 0001 2156 142X",
                "scheme": "isni",
            },
            {
                "identifier": "grid.9132.9",
                "scheme": "grid",
            },
            {"scheme": "doi", "identifier": "10.13039/100012470"},
        ],
        "acronym": "CERN",
        "name": "European Organization for Nuclear Research",
        "title": {
            "en": "European Organization for Nuclear Research",
            "fr": "Organisation européenne pour la recherche nucléaire",
        },
        "country": "CH",
        "country_name": "Switzerland",
        "location_name": "Geneva",
        "status": "active",
        "types": ["facility", "funder"],
    }


@pytest.fixture(scope="module")
def service():
    """Funders service object."""
    return current_service_registry.get("funders")


@pytest.fixture()
def indexer(service):
    """Indexer instance with correct Record class."""
    return current_indexer_registry.get("funders")


@pytest.fixture(scope="function")
def example_funder(identity, service, funder_full_data, indexer):
    """Creates and hard deletes a funder."""
    funder = service.create(identity, funder_full_data)
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
        indexer.delete(funder._record, refresh=True)
    except ObjectDeletedError:
        indexer.delete(funder_dict(), refresh=True)
