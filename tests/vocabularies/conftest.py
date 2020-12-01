# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabularies test config."""

import pytest
from invenio_indexer.api import RecordIndexer

from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.models import VocabularyType


@pytest.fixture()
def example_data():
    """Example data."""
    return {"metadata": {"title": "Test"}}


@pytest.fixture()
def example_record(db, example_data):
    """Example record."""
    vocabulary_type = VocabularyType(name="languages")
    db.session.add(vocabulary_type)
    db.session.commit()

    record = Vocabulary.create(
        example_data, vocabulary_type=vocabulary_type.id
    )
    record.commit()
    db.session.commit()
    return record


@pytest.fixture()
def indexer():
    """Indexer instance with correct Record class."""
    return RecordIndexer(
        record_cls=Vocabulary,
        record_to_index=lambda r: (r.index._name, "_doc"),
    )
