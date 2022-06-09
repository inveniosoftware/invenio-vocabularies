# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Subject API tests."""

from functools import partial

import pytest
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search_client

from invenio_vocabularies.contrib.subjects.api import Subject


@pytest.fixture()
def search_get():
    """Get a document from an index."""
    return partial(current_search_client.get, Subject.index._name, doc_type="_doc")


@pytest.fixture()
def indexer():
    """Indexer instance with correct Record class."""
    return RecordIndexer(
        record_cls=Subject,
        record_to_index=lambda r: (r.__class__.index._name, "_doc"),
    )


@pytest.fixture()
def example_subject(db, subject_full_data):
    """Example subject."""
    subj = Subject.create(subject_full_data)
    Subject.pid.create(subj)
    subj.commit()
    db.session.commit()
    return subj


def test_subject_indexing(app, db, es, example_subject, indexer, search_get):
    """Test indexing of a subject."""
    # Index document in ES
    assert indexer.index(example_subject)["result"] == "created"

    # Retrieve document from ES
    data = search_get(id=example_subject.id)

    # Loads the ES data and compare
    subj = Subject.loads(data["_source"])
    assert subj == example_subject
    assert subj.id == example_subject.id
    assert subj.revision_id == example_subject.revision_id
    assert subj.created == example_subject.created
    assert subj.updated == example_subject.updated


def test_subject_pid(app, db, example_subject):
    """Test subject pid creation."""
    subj = example_subject

    assert subj.pid.pid_value == "https://id.nlm.nih.gov/mesh/D000001"
    assert subj.pid.pid_type == "sub"
    assert Subject.pid.resolve("https://id.nlm.nih.gov/mesh/D000001")
