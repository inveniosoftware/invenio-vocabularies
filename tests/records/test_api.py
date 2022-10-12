# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Data access layer tests."""

import pytest
from jsonschema import ValidationError as SchemaValidationError
from sqlalchemy import inspect

from invenio_vocabularies.records.api import Vocabulary


def test_record_schema_validation(app, db, lang_type):
    """Record schema validation."""
    # Good data
    record = Vocabulary.create(
        {
            "id": "eng",
            "title": {"en": "English", "da": "Engelsk"},
            "description": {"en": "English", "da": "Engelsk"},
            "icon": "en",
            "props": {"akey": "a value"},
            "tags": ["recommended"],
        },
        type=lang_type,
    )
    assert record.schema

    # Bad data
    examples = [
        # title/descriptions are objects of key/string.
        {"id": "en", "title": "not a string"},
        {"id": "en", "title": {"en": 123}},
        {"id": "en", "description": "not a string"},
        # icon must be strings
        {"id": "en", "icon": 123},
        # props values must be strings
        {"id": "en", "props": {"key": 123}},
        {"id": "en", "props": {"key": {"test": "test"}}},
        # Additional properties false
        {"id": "en", "metadata": {"title": "test"}},
    ]

    for ex in examples:
        pytest.raises(SchemaValidationError, Vocabulary.create, ex)


def test_record_indexing(app, db, search, example_record, indexer, search_get):
    """Test indexing of a record."""
    # Index document in ES
    assert indexer.index(example_record)["result"] == "created"

    # Retrieve document from ES
    data = search_get(id=example_record.id)

    # Loads the ES data and compare
    record = Vocabulary.loads(data["_source"])
    assert record == example_record
    assert record.id == example_record.id
    assert record.revision_id == example_record.revision_id
    assert record.created == example_record.created
    assert record.updated == example_record.updated

    # Check system fields - i.e reading related type object from
    assert record == example_record
    assert record.type.id == "languages"
    assert record.type.pid_type == "lng"

    # Check that object was recrated without hitting DB
    assert inspect(record.type).persistent is False
    Vocabulary.type.session_merge(record)
    assert inspect(record.type).persistent is True


def test_record_pids(app, db, lang_type, lic_type):
    """Test record pid creation."""
    record = Vocabulary.create(
        {"id": "eng", "title": {"en": "English", "da": "Engelsk"}}, type=lang_type
    )
    Vocabulary.pid.create(record)
    assert record.type == lang_type
    assert record.pid.pid_value == "eng"
    assert record.pid.pid_type == "lng"
    assert Vocabulary.pid.resolve(("languages", "eng"))

    record = Vocabulary.create(
        {"id": "cc-by", "title": {"en": "CC-BY", "da": "CC-BY"}}, type=lic_type
    )
    Vocabulary.pid.create(record)
    assert record.type == lic_type
    assert record.pid.pid_value == "cc-by"
    assert record.pid.pid_type == "lic"
    assert Vocabulary.pid.resolve(("licenses", "cc-by"))
