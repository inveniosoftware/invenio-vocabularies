# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names API tests."""

from copy import deepcopy
from functools import partial

import pytest
from invenio_records.systemfields.relations.errors import InvalidRelationValue
from invenio_search import current_search_client
from jsonschema import ValidationError as SchemaValidationError

from invenio_vocabularies.contrib.names.api import Name


@pytest.fixture()
def search_get():
    """Get a document from an index."""
    return partial(current_search_client.get, Name.index._name)


@pytest.fixture()
def example_name(db, name_full_data, example_affiliation):
    """Example name."""
    api_name = deepcopy(name_full_data)
    pid = api_name.pop("id")  # at API level it's passed as an arg
    name = Name.create(api_name, pid=pid)
    name.commit()
    db.session.commit()
    return name


def test_name_schema_validation(app, db, example_name):
    """Name schema validation."""
    # valid data
    name = example_name

    assert name.schema == "local://names/name-v1.0.0.json"
    assert name.pid
    assert name.id

    # invalid data
    examples = [
        # identifiers are objects of key/string.
        {"name": "Doe, John", "identifiers": "0000-0001-8135-3489"},
        {"name": "Doe, John", "identifiers": ["0000-0001-8135-3489"]},
        {"name": "Doe, John", "identifiers": {"0000-0001-8135-3489"}},
        # names must be a string
        {"name": 123},
        {"family_name": 123, "given_name": "John"},
        {"family_name": "Doe", "given_name": 123},
        # affiliations are objects of key/string.
        {"name": "Doe, John", "affiliations": "cern"},
        {"name": "Doe, John", "affiliations": ["cern"]},
        {"name": "Doe, John", "affiliations": {"cern"}},
    ]

    for ex in examples:
        pytest.raises(SchemaValidationError, Name.create, ex)

    # test an affiliation that does not exist in the db
    invalid_aff = {"name": "Doe, John", "affiliations": [{"id": "invalid"}]}
    invalid_name = Name.create(invalid_aff)
    pytest.raises(InvalidRelationValue, invalid_name.commit)


def test_name_indexing(app, db, search, example_name, indexer, search_get):
    """Test indexing of a name."""
    # Index document in ES
    assert indexer.index(example_name)["result"] == "created"

    # Retrieve document from ES
    data = search_get(id=example_name.id)

    # Loads the ES data and compare
    name = Name.loads(data["_source"])
    assert name == example_name
    assert name.id == example_name.id
    assert name.revision_id == example_name.revision_id
    assert name.created == example_name.created
    assert name.updated == example_name.updated


def test_name_pid(app, db, example_name):
    """Test name pid creation."""
    assert example_name.pid.pid_value == "0000-0001-8135-3489"
