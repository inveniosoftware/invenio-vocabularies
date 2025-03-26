# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2024 California Institute of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

# Monkey patch Werkzeug 2.1, needed to import flask_security.login_user
# Flask-Login uses the safe_str_cmp method which has been removed in Werkzeug
# 2.1. Flask-Login v0.6.0 (yet to be released at the time of writing) fixes the
# issue. Once we depend on Flask-Login v0.6.0 as the minimal version in
# Flask-Security-Invenio/Invenio-Accounts we can remove this patch again.
try:
    # Werkzeug <2.1
    from werkzeug import security

    security.safe_str_cmp
except AttributeError:
    # Werkzeug >=2.1
    import hmac

    from werkzeug import security

    security.safe_str_cmp = hmac.compare_digest


import pytest
from flask_principal import Identity, Need, UserNeed
from flask_security import login_user
from flask_security.utils import hash_password
from invenio_access.permissions import (
    ActionUsers,
    any_user,
    superuser_access,
    system_process,
)
from invenio_access.proxies import current_access
from invenio_accounts.proxies import current_datastore
from invenio_accounts.testutils import login_user_via_session
from invenio_app.factory import create_api as _create_api
from invenio_cache import current_cache

from invenio_vocabularies.datastreams import StreamEntry
from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.models import VocabularyType

pytest_plugins = ("celery.contrib.pytest",)


@pytest.fixture(scope="module")
def h():
    """Accept JSON headers."""
    return {"accept": "application/json"}


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    return {
        "invenio_db.models": [
            "mock_module = mock_module.models",
        ],
        "invenio_jsonschemas.schemas": [
            "mock_module = mock_module.jsonschemas",
        ],
        "invenio_search.mappings": [
            "records = mock_module.mappings",
        ],
    }


@pytest.fixture(scope="module")
def app_config(app_config):
    """Mimic an instance's configuration."""
    app_config["JSONSCHEMAS_HOST"] = "localhost"
    app_config["BABEL_DEFAULT_LOCALE"] = "en"
    app_config["I18N_LANGUAGES"] = [("da", "Danish")]
    app_config["RECORDS_REFRESOLVER_CLS"] = (
        "invenio_records.resolver.InvenioRefResolver"
    )
    app_config["RECORDS_REFRESOLVER_STORE"] = (
        "invenio_jsonschemas.proxies.current_refresolver_store"
    )
    app_config["THEME_FRONTPAGE"] = False
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


@pytest.fixture(scope="module")
def identity():
    """Simple identity to interact with the service."""
    i = Identity(1)
    i.provides.add(UserNeed(1))
    i.provides.add(any_user)
    i.provides.add(system_process)
    return i


@pytest.fixture(scope="module")
def superuser_identity():
    """Super user identity to interact with the services."""
    i = Identity(2)
    i.provides.add(UserNeed(2))
    i.provides.add(any_user)
    i.provides.add(system_process)
    i.provides.add(superuser_access)
    return i


@pytest.fixture(scope="module")
def service(app):
    """Vocabularies service object."""
    return app.extensions["invenio-vocabularies"].vocabularies_service


@pytest.fixture()
def lang_type(db):
    """Get a language vocabulary type."""
    v = VocabularyType.create(id="languages", pid_type="lng")
    db.session.commit()
    return v


@pytest.fixture(scope="function")
def lang_data():
    """Example data."""
    return {
        "id": "eng",
        "title": {"en": "English", "da": "Engelsk"},
        "description": {"en": "English description", "da": "Engelsk beskrivelse"},
        "icon": "file-o",
        "props": {
            "akey": "avalue",
        },
        "tags": ["recommended"],
        "type": "languages",
    }


@pytest.fixture()
def lang_data2(lang_data):
    """Example data for testing invalid cases."""
    data = dict(lang_data)
    data["id"] = "new"
    return data


@pytest.fixture()
def non_searchable_lang_data(lang_data):
    """Example data for testing unlisted cases."""
    data = dict(lang_data)
    data["tags"] = ["unlisted", "recommended"]
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
        data=dict(**example_data, vocabulary_type_id=vocabulary_type_languages.id),
    )

    Vocabulary.index.refresh()  # Refresh the index
    return record


@pytest.fixture(scope="function")
def lang_data_many(lang_type, lang_data, service, identity):
    """Create many language vocabulary."""
    lang_ids = ["fr", "tr", "gr", "ger", "es"]
    data = dict(lang_data)

    for lang_id in lang_ids:
        data["id"] = lang_id
        service.create(identity, data)
    Vocabulary.index.refresh()  # Refresh the index
    return lang_ids


@pytest.fixture()
def user(app, db):
    """Create example user."""
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        _user = datastore.create_user(
            email="info@inveniosoftware.org",
            password=hash_password("password"),
            active=True,
        )
    db.session.commit()
    return _user


@pytest.fixture()
def role(app, db):
    """Create some roles."""
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        role = datastore.create_role(name="admin", description="admin role")

    db.session.commit()
    return role


@pytest.fixture()
def client_with_credentials(db, client, user, role):
    """Log in a user to the client."""
    current_datastore.add_role_to_user(user, role)
    action = current_access.actions["superuser-access"]
    db.session.add(ActionUsers.allow(action, user_id=user.id))

    login_user(user, remember=True)
    login_user_via_session(client, email=user.email)

    return client


@pytest.fixture()
def dict_ror_entry():
    """An example entry from ROR v2 Data Dump."""
    return StreamEntry(
        {
            "locations": [
                {
                    "geonames_id": 5381396,
                    "geonames_details": {
                        "country_code": "US",
                        "country_name": "United States",
                        "lat": 34.14778,
                        "lng": -118.14452,
                        "name": "Pasadena",
                    },
                }
            ],
            "established": 1891,
            "external_ids": [
                {
                    "type": "fundref",
                    "all": ["100006961", "100009676"],
                    "preferred": "100006961",
                },
                {
                    "type": "grid",
                    "all": ["grid.20861.3d"],
                    "preferred": "grid.20861.3d",
                },
                {"type": "isni", "all": ["0000 0001 0706 8890"], "preferred": None},
                {"type": "wikidata", "all": ["Q161562"], "preferred": None},
            ],
            "id": "https://ror.org/05dxps055",
            "domains": [],
            "links": [
                {"type": "website", "value": "http://www.caltech.edu/"},
                {
                    "type": "wikipedia",
                    "value": "http://en.wikipedia.org/wiki/California_Institute_of_Technology",
                },
            ],
            "names": [
                {"value": "CIT", "types": ["acronym"], "lang": None},
                {
                    "value": "California Institute of Technology",
                    "types": ["ror_display", "label"],
                    "lang": "en",
                },
                {"value": "Caltech", "types": ["alias"], "lang": None},
                {
                    "value": "Instituto de Tecnología de California",
                    "types": ["label"],
                    "lang": "es",
                },
            ],
            "relationships": [
                {
                    "label": "Caltech Submillimeter Observatory",
                    "type": "child",
                    "id": "https://ror.org/01e6j9276",
                },
                {
                    "label": "Infrared Processing and Analysis Center",
                    "type": "child",
                    "id": "https://ror.org/05q79g396",
                },
                {
                    "label": "Joint Center for Artificial Photosynthesis",
                    "type": "child",
                    "id": "https://ror.org/05jtgpc57",
                },
                {
                    "label": "Keck Institute for Space Studies",
                    "type": "child",
                    "id": "https://ror.org/05xkke381",
                },
                {
                    "label": "Jet Propulsion Laboratory",
                    "type": "child",
                    "id": "https://ror.org/027k65916",
                },
                {
                    "label": "Institute for Collaborative Biotechnologies",
                    "type": "child",
                    "id": "https://ror.org/04kz4p343",
                },
                {
                    "label": "Resnick Sustainability Institute",
                    "type": "child",
                    "id": "https://ror.org/04bxjes65",
                },
            ],
            "status": "active",
            "types": ["education", "funder"],
            "admin": {
                "created": {"date": "2018-11-14", "schema_version": "1.0"},
                "last_modified": {"date": "2024-05-13", "schema_version": "2.0"},
            },
        },
    )


# FIXME: https://github.com/inveniosoftware/pytest-invenio/issues/30
# Without this, success of test depends on the tests order
@pytest.fixture()
def cache():
    """Empty cache."""
    try:
        yield current_cache
    finally:
        current_cache.clear()
