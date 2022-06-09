# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Basic tests for the mock module to ensure it works properly."""

from functools import partial

import pytest
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search_client
from mock_module.api import Record


#
# Fixtures
#
@pytest.fixture()
def mock_record(app, db, example_record):
    """An example mock record."""
    return Record.create({}, metadata={"title": "Test", "languages": [{"id": "eng"}]})


@pytest.fixture()
def mock_indexer():
    """Get an indexer for mock records."""
    return RecordIndexer(
        record_cls=Record,
        record_to_index=lambda r: (r.__class__.index._name, "_doc"),
    )


@pytest.fixture()
def mock_search():
    """Get a search client."""
    return partial(current_search_client.get, Record.index._name, doc_type="_doc")


#
# Tests
#
def test_mock_record(mock_record):
    """Basic smoke test."""
    assert mock_record.schema
    assert mock_record.pid


def test_linked_record(mock_record, example_record):
    """Linked record fetching."""
    # Dereference the linked language record
    lang_record = list(mock_record.relations.languages())[0]
    assert lang_record == example_record


def test_dereferencing(mock_record):
    """Record dereferencing."""
    # Dereference the linked language record
    mock_record.relations.languages.dereference()
    deferenced_lang_record = mock_record.metadata["languages"][0]
    # Test that only part of the language record is denormalised.
    assert sorted(deferenced_lang_record.keys()) == ["@v", "id", "title"]


def test_dumping(mock_record, example_record):
    """Record schema validation."""
    # Create a record linked to a language record.
    lang = mock_record.dumps()["metadata"]["languages"][0]
    assert lang == {
        "id": "eng",
        "title": {"da": "Engelsk", "en": "English"},
        "@v": str(example_record.id) + "::" + str(example_record.revision_id),
    }


def test_indexing(mock_record, mock_indexer, mock_search, example_record):
    # Index document in ES
    assert mock_indexer.index(mock_record)["result"] == "created"

    # Retrieve document from ES and load the source
    data = mock_search(id=mock_record.id)
    record = Record.loads(data["_source"])

    # Getting the language records should work:
    lang_record = list(record.relations.languages())[0]
    assert lang_record == example_record

    # Dereferencing also works
    record.relations.languages.dereference()
    deferenced_lang_record = mock_record.metadata["languages"][0]
    assert sorted(deferenced_lang_record.keys()) == ["@v", "id", "title"]
