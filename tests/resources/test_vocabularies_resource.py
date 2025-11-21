# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2025 Northwestern University.
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
def example_licenses_data():
    """Example data for records."""
    return [
        {
            "id": "cc-by",
            "title": {"en": "Creative Commons Attribution"},
            "type": "licenses",
        },
        {"id": "cc0", "title": {"en": "Creative Commons Zero"}, "type": "licenses"},
    ]


@pytest.fixture(scope="module")
def example_licenses_records(database, identity, service, example_licenses_data):
    """Create some example records."""
    service.create_type(identity, "licenses", "lic")
    records = [service.create(identity, data) for data in example_licenses_data]
    Vocabulary.index.refresh()
    return records


@pytest.fixture(scope="module")
def example_resourcetypes_data():
    """Example data for records."""
    return [
        {"id": "text", "title": {"en": "Text"}, "type": "resourcetypes"},
        {
            "id": "data",
            "title": {"en": "Data"},
            "type": "resourcetypes",
            "tags": ["recommended"],
        },
    ]


@pytest.fixture(scope="module")
def example_resourcetypes_records(
    database, identity, service, example_resourcetypes_data
):
    """Create some example records."""
    service.create_type(identity, "resourcetypes", "rt")
    records = [service.create(identity, data) for data in example_resourcetypes_data]
    Vocabulary.index.refresh()
    return records


#
# Tests
#
# For historical reasons,
#   read tests are done against /api/vocabularies/licenses/
#   search tests are done against /api/vocabularies/resourcetypes/
def test_read(client, example_licenses_records, h):
    """Test the endpoint to retrieve a single item."""
    id_ = example_licenses_records[0].id

    res = client.get(f"/vocabularies/licenses/{id_}", headers=h)

    assert 200 == res.status_code
    assert id_ == res.json["id"]
    expected_links = {"self": "https://127.0.0.1:5000/api/vocabularies/licenses/cc-by"}
    assert expected_links == res.json["links"]


def test_read_not_found(client, example_licenses_records, h):
    """Test not found."""
    # invalid id
    res = client.get("/vocabularies/licenses/invalid-id", headers=h)
    assert 404 == res.status_code

    # invalid type (wrong type for pid)
    id_ = example_licenses_records[0].id
    res = client.get(f"/vocabularies/invalid/{id_}", headers=h)
    assert 404 == res.status_code


def test_search(client, example_resourcetypes_records, h):
    """Test a successful search."""
    res = client.get("/vocabularies/resourcetypes", headers=h)

    assert 200 == res.status_code
    assert 2 == res.json["hits"]["total"]
    assert "title" == res.json["sortBy"]
    expected_links = {
        "self": (
            "https://127.0.0.1:5000/api/vocabularies/resourcetypes"
            "?page=1&size=25&sort=title"
        )
    }
    assert expected_links == res.json["links"]


def test_search_invalid_type(client, example_resourcetypes_records, h):
    """Test invalid type."""
    # invalid type
    res = client.get("/vocabularies/invalid", headers=h)
    assert 404 == res.status_code
    # trailing slash
    res = client.get("/vocabularies/invalid/", headers=h)
    assert 404 == res.status_code


def test_search_type_as_query_arg(client, lang_type, example_resourcetypes_records, h):
    """Test passing an invalid query parameter."""
    # Ensure we cannot pass invalid query parameters
    res = client.get("/vocabularies/resourcetypes?invalid=test", headers=h)
    assert 200 == res.status_code
    assert "invalid" not in res.json["links"]["self"]

    # It should not be possible to pass 'type' in query args (because it's in
    # the URL route instead)
    res = client.get(f"/vocabularies/resourcetypes?type={lang_type.id}", headers=h)
    assert 200 == res.status_code
    assert lang_type.id not in res.json["links"]["self"]
    assert "type=" not in res.json["links"]["self"]
    assert "resourcetypes" in res.json["links"]["self"]


def test_search_query_q(client, example_resourcetypes_records, h):
    """Test a successful search."""
    # Test query (q=)
    res = client.get(f"/vocabularies/resourcetypes?q=title.en:text", headers=h)
    assert 200 == res.status_code
    assert 1 == res.json["hits"]["total"]
    assert "bestmatch" == res.json["sortBy"]

    # Test sort
    res = client.get("/vocabularies/resourcetypes?q=*&sort=bestmatch", headers=h)
    assert 200 == res.status_code
    assert "bestmatch" == res.json["sortBy"]

    # Test size
    res = client.get("/vocabularies/resourcetypes?size=1&page=1", headers=h)
    assert 200 == res.status_code
    assert 2 == res.json["hits"]["total"]
    assert 1 == len(res.json["hits"]["hits"])
    assert "next" in res.json["links"]


def test_search_tags_filter(client, example_resourcetypes_records, h):
    """Test filter on tags."""
    # Test query (q=)
    res = client.get("/vocabularies/resourcetypes?tags=recommended", headers=h)
    assert 200 == res.status_code
    assert 1 == res.json["hits"]["total"]
