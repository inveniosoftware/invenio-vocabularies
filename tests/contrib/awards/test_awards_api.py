# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Awards API tests."""

from copy import deepcopy
from functools import partial

import pytest
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search_client
from jsonschema import ValidationError as SchemaValidationError

from invenio_vocabularies.contrib.awards.api import Award


@pytest.fixture()
def search_get():
    """Get a document from an index."""
    return partial(current_search_client.get, Award.index._name)


@pytest.fixture()
def example_award(db, award_full_data, example_funder_ec):
    """Example award."""
    api_award = deepcopy(award_full_data)
    pid = api_award.pop("id")  # at API level it's passed as an arg
    awa = Award.create(api_award, pid=pid)
    awa.commit()
    db.session.commit()
    return awa


def test_award_schema_validation(app, example_award):
    """Award schema validation."""
    # valid data
    awa = example_award

    assert awa.schema == "local://awards/award-v1.0.0.json"
    assert awa.pid
    assert awa.id

    # invalid data
    examples = [
        # title are objects of key/string.
        {"title": "not a dict"},
        {"title": {"en": 123}},
        # identifiers are objects of key/string.
        {"identifiers": "03yrm5c26"},
        {"identifiers": ["03yrm5c26"]},
        {"identifiers": {"03yrm5c26"}},
        # number must be a string
        {"number": 123},
        # funder must be an object
        {"funder": 123},
    ]

    for ex in examples:
        pytest.raises(SchemaValidationError, Award.create, ex)


def test_award_indexing(app, example_award, indexer, search_get):
    """Test indexing of an award."""
    # Index document in ES
    assert indexer.index(example_award)["result"] == "created"

    # Retrieve document from ES
    data = search_get(id=example_award.id)

    # Loads the ES data and compare
    awa = Award.loads(data["_source"])
    assert awa == example_award
    assert awa.id == example_award.id
    assert awa.pid.pid_value == example_award.pid.pid_value
    assert awa.revision_id == example_award.revision_id
    assert awa.created == example_award.created
    assert awa.updated == example_award.updated


def test_award_pid(app, example_award):
    """Test award pid creation."""
    awa = example_award

    assert awa.pid.pid_value == "755021"
    assert Award.pid.resolve("755021") == example_award
