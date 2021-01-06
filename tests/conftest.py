# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from flask_principal import Identity, Need, UserNeed
from invenio_app.factory import create_api as _create_api

from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.models import VocabularyType
from invenio_vocabularies.services.service import VocabulariesService


@pytest.fixture(scope='module')
def app_config(app_config):
    """Mimic an instance's configuration."""
    app_config["JSONSCHEMAS_HOST"] = 'localhost'
    return app_config


@pytest.fixture()
def example_data():
    """Example data."""
    return {
        "metadata": {
            "title": {"en": "Test title", "fr": "Titre test"},
            "description": {
                "en": "Test description",
                "de": "Textbeschreibung",
            },
            "icon": "icon-identifier",
            "props": {"key": "value"},
        }
    }


@pytest.fixture(scope="module")
def celery_config():
    """Override pytest-invenio fixture."""
    return {}


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return _create_api


@pytest.fixture(scope="module")
def identity_simple():
    """Simple identity fixture."""
    i = Identity(1)
    i.provides.add(UserNeed(1))
    i.provides.add(Need(method="system_role", value="any_user"))
    return i


@pytest.fixture()
def service():
    """Vocabularies service object."""
    return VocabulariesService()


@pytest.fixture()
def example_record(db, identity_simple, service, example_data):
    """Example record."""
    vocabulary_type_languages = VocabularyType(name="languages")
    vocabulary_type_licenses = VocabularyType(name="licenses")
    db.session.add(vocabulary_type_languages)
    db.session.add(vocabulary_type_licenses)
    db.session.commit()

    record = service.create(
        identity=identity_simple,
        data=dict(
            **example_data, vocabulary_type_id=vocabulary_type_languages.id
        ),
    )

    Vocabulary.index.refresh()  # Refresh the index

    return record
