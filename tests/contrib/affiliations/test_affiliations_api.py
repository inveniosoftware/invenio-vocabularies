# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Affiliations API tests."""

from copy import deepcopy
from functools import partial

import pytest
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search_client
from jsonschema import ValidationError as SchemaValidationError

from invenio_vocabularies.contrib.affiliations.api import Affiliation


@pytest.fixture()
def search_get():
    """Get a document from an index."""
    return partial(current_search_client.get, Affiliation.index._name)


@pytest.fixture()
def indexer():
    """Indexer instance with correct Record class."""
    return RecordIndexer(
        record_cls=Affiliation,
        record_to_index=lambda r: (r.__class__.index._name, "_doc"),
    )


@pytest.fixture()
def example_affiliation(db, affiliation_full_data):
    """Example affiliation."""
    api_affiliation = deepcopy(affiliation_full_data)
    pid = api_affiliation.pop("id")
    aff = Affiliation.create(api_affiliation, pid=pid)
    aff.commit()
    db.session.commit()
    return aff


def test_affiliation_schema_validation(app, db, example_affiliation):
    """Affiliation schema validation."""
    # valid data
    aff = example_affiliation

    assert aff.schema == "local://affiliations/affiliation-v1.0.0.json"
    assert aff.pid
    assert aff.id

    # invalid data
    examples = [
        # title are objects of key/string.
        {"id": "cern", "name": "cern", "title": "not a dict"},
        {"id": "cern", "name": "cern", "title": {"en": 123}},
        # identifiers are objects of key/string.
        {"id": "cern", "name": "cern", "identifiers": "03yrm5c26"},
        {"id": "cern", "name": "cern", "identifiers": ["03yrm5c26"]},
        {"id": "cern", "name": "cern", "identifiers": {"03yrm5c26"}},
        # name must be a string
        {"id": "cern", "name": 123},
        # acronym must be a string
        {"id": "cern", "name": "cern", "acronym": 123},
    ]

    for ex in examples:
        pytest.raises(SchemaValidationError, Affiliation.create, ex)


def test_affiliation_indexing(
    app, db, search, example_affiliation, indexer, search_get
):
    """Test indexing of an affiliation."""
    # Index document in ES
    assert indexer.index(example_affiliation)["result"] == "created"

    # Retrieve document from ES
    data = search_get(id=example_affiliation.id)

    # Loads the ES data and compare
    aff = Affiliation.loads(data["_source"])
    assert aff == example_affiliation
    assert aff.id == example_affiliation.id
    assert aff.revision_id == example_affiliation.revision_id
    assert aff.created == example_affiliation.created
    assert aff.updated == example_affiliation.updated


def test_affiliation_pid(app, db, example_affiliation):
    """Test affiliation pid creation."""
    aff = example_affiliation

    assert aff.pid.pid_value == "01ggx4157"
    assert Affiliation.pid.resolve("01ggx4157")
