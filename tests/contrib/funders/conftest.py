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
from invenio_db import db
from invenio_records_resources.proxies import current_service_registry

from invenio_vocabularies.contrib.funders.api import Funder


@pytest.fixture(scope="function")
def funder_full_data():
    """Full funder data."""
    return {
        "id": "01ggx4157",
        "identifiers": [
            {
                "identifier": "000000012156142X",
                "scheme": "isni",
            },
            {
                "identifier": "grid.9132.9",
                "scheme": "grid",
            },
        ],
        "name": "CERN",
        "title": {
            "en": "European Organization for Nuclear Research",
            "fr": "Organisation européenne pour la recherche nucléaire",
        },
        "country": "CH",
    }


@pytest.fixture(scope="module")
def service():
    """Funders service object."""
    return current_service_registry.get("funders")


@pytest.fixture()
def indexer(service):
    """Indexer instance with correct Record class."""
    return service.indexer


@pytest.fixture(scope="function")
def example_funder(identity, service, funder_full_data, indexer):
    """Creates and hard deletes a funder."""
    funder = service.create(identity, funder_full_data)
    Funder.index.refresh()  # Refresh the index
    yield funder
    funder._record.delete(force=True)
    indexer.delete(funder._record, refresh=True)
    db.session.commit()
