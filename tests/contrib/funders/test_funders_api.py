# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Funders API tests."""

from copy import deepcopy
from functools import partial

import pytest
from invenio_search import current_search_client
from jsonschema import ValidationError

from invenio_vocabularies.contrib.funders.api import Funder


@pytest.fixture()
def search_get():
    """Get a document from an index."""
    return partial(current_search_client.get, Funder.index._name, doc_type="_doc")


@pytest.fixture()
def example_funder(db, funder_full_data):
    """Example funder."""
    api_funder = deepcopy(funder_full_data)
    pid = api_funder.pop("id")  # at API level it's passed as an arg
    fun = Funder.create(api_funder, pid=pid)
    fun.commit()
    db.session.commit()
    return fun


def test_funder_schema_validation(app, example_funder):
    """Funder schema validation."""
    # valid data
    fun = example_funder

    assert fun.schema == "local://funders/funder-v1.0.0.json"
    assert fun.pid
    assert fun.id

    # invalid data
    examples = [
        # name must be a string
        {"name": 123},
        # country must be a string
        {"name": "cern", "country": 123},
    ]

    for ex in examples:
        pytest.raises(ValidationError, Funder.create, ex)


def test_funder_indexing(app, example_funder, indexer, search_get):
    """Test indexing of a funder."""
    # Index document in ES
    assert indexer.index(example_funder)["result"] == "created"

    # Retrieve document from ES
    data = search_get(id=example_funder.id)

    # Loads the ES data and compare
    fun = Funder.loads(data["_source"])
    assert fun == example_funder
    assert fun.id == example_funder.id
    assert fun.pid.pid_value == example_funder.pid.pid_value
    assert fun.revision_id == example_funder.revision_id
    assert fun.created == example_funder.created
    assert fun.updated == example_funder.updated


def test_funder_pid(app, example_funder):
    """Test funder pid creation."""

    assert example_funder.pid.pid_value == "01ggx4157"
    assert Funder.pid.resolve("01ggx4157") == example_funder
