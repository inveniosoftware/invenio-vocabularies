# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Data access layer tests."""

import pytest
from invenio_search import current_search_client
from jsonschema import ValidationError
from sqlalchemy.exc import IntegrityError

from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.models import VocabularyType


def test_record_empty(app, db):
    """Test record creation."""
    # Empty record creation works, and injects a schema.
    record = Vocabulary.create({})
    db.session.commit()
    assert record.schema

    # JSONSchema validation works.
    pytest.raises(
        ValidationError, Vocabulary.create, {"metadata": {"title": 1}}
    )


def test_record_via_field(app, db):
    """Record creation via field."""
    record = Vocabulary.create({}, metadata={"title": "test"})
    assert record.metadata == {"title": "test"}


def test_vocabulary_type(app, db):
    """Vocabulary creation."""
    vocabulary_type = VocabularyType(**{"name": "test-type"})
    db.session.add(vocabulary_type)
    db.session.commit()
    record = Vocabulary.create(
        {}, metadata={"title": "test-item", "type": "test-type"}
    )
    assert record.metadata == {"title": "test-item", "type": "test-type"}


def test_record_indexing(app, db, es, example_record, indexer):
    """Test indexing of a record."""
    # Index document in ES
    assert indexer.index(example_record)["result"] == "created"

    # Retrieve document from ES
    data = current_search_client.get(
        "vocabularies-vocabulary-v1.0.0", id=example_record.id, doc_type="_doc"
    )

    # Loads the ES data and compare
    record = Vocabulary.loads(data["_source"])
    assert record == example_record
    assert record.id == example_record.id
    assert record.revision_id == example_record.revision_id
    assert record.created == example_record.created
    assert record.updated == example_record.updated
    assert record.vocabulary_type_id == example_record.vocabulary_type_id

    # Check system fields
    assert record.metadata == example_record["metadata"]


def test_record_delete_reindex(
    app, db, es, example_record, example_data, indexer
):
    """Test reindexing of a deleted record."""
    record = example_record

    # Index record
    assert indexer.index(record)["result"] == "created"

    # Delete record.
    record.delete()
    db.session.commit()
    assert indexer.delete(record)["result"] == "deleted"

    # Update record and reindex (this will cause troubles unless proper
    # optimistic concurrency control is used).
    record.undelete()
    record.commit()
    db.session.commit()
    assert indexer.index(record)["result"] == "created"


def test_record_validation(app, db):
    """Test vocabulary item validation."""
    vocabulary_type = VocabularyType(name="test")
    db.session.add(vocabulary_type)
    db.session.commit()

    def create(metadata):
        rec = Vocabulary.create(
            {"metadata": metadata}, vocabulary_type_id=vocabulary_type.id
        )
        rec.commit()
        db.session.commit()
        return rec

    def check_invalid(metadata):
        with pytest.raises(ValidationError):
            create(metadata)

    # valid items
    create({})
    create({"title": {}})
    assert create({"nonexistent": "value"}).metadata == {}

    # invalid items
    check_invalid({"title": "Title"})
    check_invalid({"title": {"not a language": "Title"}})
    check_invalid({"props": {"key": {}}})

    # missing foreign key
    with pytest.raises(IntegrityError):
        record = Vocabulary.create(
            {"metadata": {}}, vocabulary_type_id=-1
        )
        record.commit()


def test_endpoint_list(app, client, example_record):
    """Test the list endpoint."""

    res = client.get("/api/vocabularies/",
                     headers={"accept": "application/json"})

    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1


def test_endpoint_filter(app, db, client):
    """Test the list endpoint while filtering by vocabulary type."""

    vocabulary_type_1 = VocabularyType(name="type1")
    db.session.add(vocabulary_type_1)
    vocabulary_type_2 = VocabularyType(name="type2")
    db.session.add(vocabulary_type_2)
    db.session.commit()

    record1 = Vocabulary.create(
        {"metadata": {}}, vocabulary_type_id=vocabulary_type_1.id
    )
    record1.commit()
    record2 = Vocabulary.create(
        {"metadata": {}}, vocabulary_type_id=vocabulary_type_2.id
    )
    record2.commit()

    res = client.get("/api/vocabularies?vocabulary_type=type1",
                     headers={"accept": "application/json"})
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["id"] == record1.id
