# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2021 TU Wien.
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
from invenio_access.permissions import any_user, system_process
from invenio_app.factory import create_api as _create_api

from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.models import VocabularyType

pytest_plugins = ("celery.contrib.pytest", )


@pytest.fixture()
def h():
    """Accept JSON headers."""
    return {"accept": "application/json"}


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    return {
        'invenio_db.models': [
            'mock_module = mock_module.models',
        ],
        'invenio_jsonschemas.schemas': [
            'mock_module = mock_module.jsonschemas',
        ],
        'invenio_search.mappings': [
            'records = mock_module.mappings',
        ]
    }


@pytest.fixture(scope='module')
def app_config(app_config):
    """Mimic an instance's configuration."""
    app_config["JSONSCHEMAS_HOST"] = 'localhost'
    app_config["BABEL_DEFAULT_LOCALE"] = 'en'
    app_config["I18N_LANGUAGES"] = [('da', 'Danish')]
    app_config['RECORDS_REFRESOLVER_CLS'] = \
        "invenio_records.resolver.InvenioRefResolver"
    app_config['RECORDS_REFRESOLVER_STORE'] = \
        "invenio_jsonschemas.proxies.current_refresolver_store"
    return app_config


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


@pytest.fixture(scope='module')
def identity():
    """Simple identity to interact with the service."""
    i = Identity(1)
    i.provides.add(UserNeed(1))
    i.provides.add(any_user)
    i.provides.add(system_process)
    return i


@pytest.fixture(scope='module')
def service(app):
    """Vocabularies service object."""
    return app.extensions['invenio-vocabularies'].service


@pytest.fixture()
def lang_type(db):
    """Get a language vocabulary type."""
    return VocabularyType.create(id='languages', pid_type='lng')


@pytest.fixture(scope='module')
def lang_data():
    """Example data."""
    return {
        'id': 'eng',
        'title': {'en': 'English', 'da': 'Engelsk'},
        'description': {
            'en': 'English description',
            'da': 'Engelsk beskrivelse'
        },
        'icon': 'file-o',
        'props': {
            'akey': 'avalue',
        },
        'tags': ['recommended'],
        'type': 'languages',
    }


@pytest.fixture()
def lang_data2(lang_data):
    """Example data for testing invalid cases."""
    data = dict(lang_data)
    data['id'] = 'new'
    return data


@pytest.fixture()
def example_record(db, identity, service, example_data):
    """Example record."""
    vocabulary_type_languages = VocabularyType(name="languages")
    vocabulary_type_licenses = VocabularyType(name="licenses")
    db.session.add(vocabulary_type_languages)
    db.session.add(vocabulary_type_licenses)
    db.session.commit()

    record = service.create(
        identity=identity,
        data=dict(
            **example_data, vocabulary_type_id=vocabulary_type_languages.id
        ),
    )

    Vocabulary.index.refresh()  # Refresh the index

    return record
