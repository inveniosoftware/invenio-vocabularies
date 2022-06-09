# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the vocabulary service facets."""

import pytest

from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.services.facets import VocabularyLabels


@pytest.fixture(scope="module")
def example_data():
    """Example data."""
    return [
        {
            "id": "eng",
            "title": {"en": "English", "da": "Engelsk"},
            "type": "languages",
        },
        {
            "id": "spa",
            "title": {"en": "Spanish", "da": "Spansk"},
            "type": "languages",
        },
        {
            "id": "fra",
            "title": {"en": "French", "da": "Fransk"},
            "type": "languages",
        },
    ]


@pytest.fixture(scope="module")
def example_records(database, identity, service, example_data):
    """Create some example records."""
    service.create_type(identity, "languages", "lng")
    records = []
    for data in example_data:
        records.append(service.create(identity, data))

    Vocabulary.index.refresh()
    return records


def _assert_vocabs(labels_instance):
    labels = labels_instance(["eng", "spa"])

    assert labels["eng"] == "English"
    assert labels["spa"] == "Spanish"


def test_vocabulary_label_cache(example_records):
    # Uses example record to have two languages created on the vocabulary
    labels_instance = VocabularyLabels(vocabulary="languages", cache=True)
    _assert_vocabs(labels_instance)


def test_vocabulary_label_no_cache(example_records):
    # Uses example record to have two languages created on the vocabulary
    labels_instance = VocabularyLabels(vocabulary="languages", cache=False)
    _assert_vocabs(labels_instance)


def test_vocabulary_label_not_found(example_records):
    # Uses example record to have two languages created on the vocabulary
    labels_instance = VocabularyLabels(vocabulary="languages", cache=True)
    labels = labels_instance(["eng", "glg"])

    assert labels["eng"] == "English"
    assert not labels.get("glg")  # search wont fail
