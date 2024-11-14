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
from invenio_indexer.api import RecordIndexer
from invenio_records_resources.proxies import current_service_registry

from invenio_vocabularies.contrib.names.api import Name


@pytest.fixture(scope="module")
def service():
    """Names service object."""
    return current_service_registry.get("names")


@pytest.fixture(scope="module")
def affiliations_service():
    """Names service object."""
    return current_service_registry.get("affiliations")


@pytest.fixture()
def example_affiliation(db, identity, affiliations_service):
    """Example affiliation."""
    aff = affiliations_service.create(
        identity,
        {"id": "cern", "name": "European Organization for Nuclear Research"},
    )
    affiliations_service.record_cls.index.refresh()
    yield aff
    aff._record.delete(force=True)
    affiliations_service.indexer.delete(aff._record, refresh=True)
    db.session.commit()


@pytest.fixture(scope="function")
def name_full_data():
    """Full name data."""
    return {
        "id": "0000-0001-8135-3489",
        "name": "Doe, John",
        "given_name": "John",
        "family_name": "Doe",
        "identifiers": [
            {"identifier": "0000-0001-8135-3489", "scheme": "orcid"},
            {"identifier": "gnd:4079154-3", "scheme": "gnd"},
        ],
        "affiliations": [{"id": "cern"}, {"name": "CustomORG"}],
    }


@pytest.fixture(scope="function")
def non_searchable_name_data():
    """Full name data."""
    return {
        "id": "0000-0001-8135-3489",
        "name": "Doe, John",
        "given_name": "John",
        "family_name": "Doe",
        "identifiers": [
            {"identifier": "0000-0001-8135-3489", "scheme": "orcid"},
            {"identifier": "gnd:4079154-3", "scheme": "gnd"},
        ],
        "affiliations": [{"id": "cern"}, {"name": "CustomORG"}],
        "tags": ["unlisted"],
    }


@pytest.fixture(scope="module")
def indexer():
    """Indexer instance with correct Record class."""
    return RecordIndexer(
        record_cls=Name,
        record_to_index=lambda r: (r.__class__.index._name, "_doc"),
    )
