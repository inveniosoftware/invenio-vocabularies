# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
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

from invenio_vocabularies.contrib.affiliations.api import Affiliation
from invenio_vocabularies.contrib.affiliations.models import AffiliationsMetadata


@pytest.fixture(scope="module")
def service():
    """Names service object."""
    return current_service_registry.get("names")


@pytest.fixture(scope="module")
def affiliations_service():
    """Names service object."""
    return current_service_registry.get("affiliations")


@pytest.fixture()
def example_affiliation(db, identity, affiliations_service, aff_indexer):
    """Example affiliation."""
    aff = affiliations_service.create(
        identity,
        {"id": "cern", "name": "European Organization for Nuclear Research"},
    )
    Affiliation.index.refresh()

    aff_id = aff._record.id
    index = type("index", (), {"_name": aff._record.index._name})
    aff_dict = type(
        "",
        (),
        {
            "index": index(),
            "id": aff._record.id,
            "revision_id": aff._record.revision_id,
        },
    )

    yield aff

    db.session.query(AffiliationsMetadata).filter(
        AffiliationsMetadata.id == aff_id
    ).delete()

    try:
        aff_indexer.delete(aff._record, refresh=True)
    except ObjectDeletedError:
        aff_indexer.delete(aff_dict(), refresh=True)


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


@pytest.fixture()
def aff_indexer():
    """Indexer instance with correct Record class."""
    return current_indexer_registry.get("affiliations")
