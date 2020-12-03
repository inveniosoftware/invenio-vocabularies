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
from flask_principal import Identity
from invenio_access import any_user
from invenio_indexer.api import RecordIndexer

from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.models import VocabularyType
from invenio_vocabularies.services.records.service import Service


@pytest.fixture()
def example_data():
    """Example data."""
    return {
        "metadata": {
            "title": {
                "en": "Test title",
                "fr": "Titre test"
            },
            "description": {
                "en": "Test description",
                "de": "Textbeschreibung"
            },
            "icon": "icon-identifier",
            "props": {
                "key": "value"
            }
        }
    }


@pytest.fixture()
def identity():
    """Simple identity to interact with the service."""
    identity = Identity(1)
    identity.provides.add(any_user)
    return identity


@pytest.fixture()
def service():
    """Vocabularies service object."""
    return Service()


@pytest.fixture()
def example_record(db, identity, service, example_data):
    """Example record."""
    vocabulary_type = VocabularyType(name="languages")
    db.session.add(vocabulary_type)
    db.session.commit()

    record = service.create(
        identity=identity, data=dict(
            **example_data,
            vocabulary_type_id=vocabulary_type.id
        )
    )

    return record


@pytest.fixture()
def indexer():
    """Indexer instance with correct Record class."""
    return RecordIndexer(
        record_cls=Vocabulary,
        record_to_index=lambda r: (r._record.index._name, "_doc"),
    )
