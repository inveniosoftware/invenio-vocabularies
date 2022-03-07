# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Funders API tests."""

from functools import partial

import pytest
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search_client
from jsonschema import ValidationError

from invenio_vocabularies.contrib.funders.api import Funder


@pytest.fixture()
def search_get():
    """Get a document from an index."""
    return partial(
        current_search_client.get, Funder.index._name, doc_type="_doc"
    )


@pytest.fixture()
def indexer():
    """Indexer instance with correct Record class."""
    return RecordIndexer(
        record_cls=Funder,
        record_to_index=lambda r: (r.__class__.index._name, "_doc"),
    )


@pytest.fixture()
def example_funder(db, funder_full_data):
    """Example funder."""
    fun = Funder.create(funder_full_data)
    Funder.pid.create(fun)
    fun.commit()
    db.session.commit()
    return fun


def test_funder_schema_validation(app, db, example_funder):
    """Funder schema validation."""
    # valid data
    fun = example_funder

    assert fun.schema == "local://funders/funder-v1.0.0.json"
    assert fun.pid
    assert fun.id

    # invalid data
    examples = [
        # name must be a string
        {"id": "cern", "name": 123},
        # country must be a string
        {"id": "cern", "name": "cern", "country": 123}
    ]

    for ex in examples:
        pytest.raises(ValidationError, Funder.create, ex)


def test_funder_indexing(
    app, db, es, example_funder, indexer, search_get
):
    """Test indexing of a funder."""
    # Index document in ES
    assert indexer.index(example_funder)["result"] == "created"

    # Retrieve document from ES
    data = search_get(id=example_funder.id)

    # Loads the ES data and compare
    fun = Funder.loads(data["_source"])
    assert fun == example_funder
    assert fun.id == example_funder.id
    assert fun.revision_id == example_funder.revision_id
    assert fun.created == example_funder.created
    assert fun.updated == example_funder.updated


def test_funder_pid(app, db, example_funder):
    """Test funder pid creation."""
    fun = example_funder

    assert fun.pid.pid_value == "fund"
    assert fun.pid.pid_type == "fun"
    assert Funder.pid.resolve("fund")
