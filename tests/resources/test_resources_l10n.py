# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Resources layer tests."""

import pytest

from invenio_vocabularies.records.api import Vocabulary


#
# Fixtures
#
@pytest.fixture(scope="module")
def example_data():
    """Example data for records."""
    return {
        "id": "text",
        "title": {
            "en": "Text",
            "da": "Tekst",
        },
        "description": {
            "en": "Publications",
            "da": "Publikationer",
        },
        "icon": "file-o",
        "props": {},
        "type": "resourcetypes2",
    }


@pytest.fixture(scope="module")
def example_record(database, identity, service, example_data):
    """Create a vocabulary record."""
    service.create_type(identity, "resourcetypes2", "rt2")
    item = service.create(identity, example_data)
    Vocabulary.index.refresh()
    return item


@pytest.fixture()
def prefix():
    """API prefix."""
    return "/vocabularies/resourcetypes2"


@pytest.fixture()
def h():
    """Header for localised versions."""
    return {"accept": "application/vnd.inveniordm.v1+json"}


@pytest.fixture(scope="module")
def expected_da():
    """Expected serialization when danish chosen."""
    return {
        "id": "text",
        "title_l10n": "Tekst",
        "description_l10n": "Publikationer",
        "icon": "file-o",
        "props": {},
    }


@pytest.fixture(scope="module")
def expected_en():
    """Expected serialization when english chosen."""
    return {
        "id": "text",
        "title_l10n": "Text",
        "description_l10n": "Publications",
        "icon": "file-o",
        "props": {},
    }


#
# Tests
#
def test_get(client, example_record, h, prefix, expected_da, expected_en):
    """Test the endpoint to retrieve a single item."""
    id_ = example_record.id

    # Default locale
    res = client.get(f"{prefix}/{id_}", headers=h)
    assert res.json == expected_en

    # Choose via querystring (?ln=da)
    res = client.get(f"{prefix}/{id_}?ln=da", headers=h)
    assert res.json == expected_da
    res = client.get(f"{prefix}/{id_}?ln=en", headers=h)
    assert res.json == expected_en

    # Choose via header
    h["accept-language"] = "da"
    res = client.get(f"{prefix}/{id_}", headers=h)
    assert res.json == expected_da
    h["accept-language"] = "en"
    res = client.get(f"{prefix}/{id_}", headers=h)
    assert res.json == expected_en


def test_search(client, example_record, h, prefix, expected_da, expected_en):
    """Test search result serialization."""
    expected_en = {"hits": {"hits": [expected_en], "total": 1}}
    expected_da = {"hits": {"hits": [expected_da], "total": 1}}

    # Default locale
    res = client.get(f"{prefix}", headers=h)
    assert res.json == expected_en

    # Choose via querystring (?ln=da)
    res = client.get(f"{prefix}?ln=da", headers=h)
    assert res.json == expected_da
    res = client.get(f"{prefix}?ln=en", headers=h)
    assert res.json == expected_en

    # Choose via header
    h["accept-language"] = "da"
    res = client.get(f"{prefix}", headers=h)
    assert res.json == expected_da
    h["accept-language"] = "en"
    res = client.get(f"{prefix}", headers=h)
    assert res.json == expected_en
