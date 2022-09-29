# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabularies test config."""

from functools import partial

import pytest
from invenio_db import db
from invenio_indexer.api import RecordIndexer
from invenio_search import current_search_client

from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.models import VocabularyType


@pytest.fixture()
def indexer():
    """Indexer instance with correct Record class."""
    return RecordIndexer(
        record_cls=Vocabulary,
        record_to_index=lambda r: (r.__class__.index._name, "_doc"),
    )


@pytest.fixture()
def search_get():
    """Get a document from an index."""
    return partial(current_search_client.get, Vocabulary.index._name)


@pytest.fixture()
def lic_type():
    """Get a language vocabulary type."""
    return VocabularyType.create(id="licenses", pid_type="lic")


@pytest.fixture()
def example_data():
    """Example data."""
    return {
        "id": "eng",
        "title": {"en": "English", "da": "Engelsk"},
        "description": {"en": "Text", "da": "Tekst"},
        "icon": "file-o",
        "props": {
            "datacite_type": "Text",
        },
    }


@pytest.fixture()
def example_record(db, example_data, lang_type):
    """Example record."""
    record = Vocabulary.create(example_data, type=lang_type)
    Vocabulary.pid.create(record)
    record.commit()
    db.session.commit()
    return record
