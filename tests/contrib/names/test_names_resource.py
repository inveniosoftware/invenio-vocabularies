# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the name vocabulary resource."""

import json

import pytest

from invenio_vocabularies.contrib.names.api import Name


@pytest.fixture(scope="module")
def prefix():
    """API prefix."""
    return "names"


@pytest.fixture()
def names_data():
    """Full name data."""
    return [
        {
            "id": "0000-0001-8135-3489",
            "given_name": "Niels John",
            "family_name": "Davidson",
            "name": "Davidson, Niels John",
            "identifiers": [
                {
                    "scheme": "orcid",
                    "identifier": "0000-0001-8135-3489",
                }
            ],
            "affiliations": [{"name": "CERN"}],
        },
        {
            "id": "0000-0002-8438-3752",
            "given_name": "Dwäyne",
            "family_name": "Johnsœn",
            "name": "Johnsœn, Dwäyne",
            "identifiers": [
                {
                    "scheme": "orcid",
                    "identifier": "0000-0002-8438-3752",
                }
            ],
            "affiliations": [{"name": "CERN"}],
        },
        {
            "id": "0000-0002-0816-7126",
            "given_name": "John",
            "family_name": "Cena",
            "name": "Cena, John",
            "identifiers": [
                {
                    "scheme": "orcid",
                    "identifier": "0000-0002-0816-7126",
                }
            ],
            "affiliations": [{"name": "WWE"}],
        },
    ]


@pytest.fixture()
def example_multiple_names(
    app, db, search_clear, identity, service, names_data, example_affiliation
):
    """Example multiple names."""
    names = []
    for i in range(len(names_data)):
        names.append(service.create(identity, names_data[i]))
        Name.index.refresh()  # Refresh the index

    return names


@pytest.fixture()
def example_name(
    app, db, search_clear, identity, service, name_full_data, example_affiliation
):
    """Example name."""
    name = service.create(identity, name_full_data)
    Name.index.refresh()  # Refresh the index

    return name


def test_non_authenticated(client, prefix, example_name, h):
    """Test non-authenticated access."""
    # Search
    res = client.get(prefix)
    assert res.status_code == 403

    id_ = example_name.id

    # Read
    res = client.get(f"{prefix}/{id_}", headers=h)
    assert res.status_code == 403

    # Resolve
    res = client.get(f"{prefix}/orcid/0000-0001-8135-3489", headers=h)
    assert res.status_code == 403


def test_names_invalid(client_with_credentials, h, prefix):
    """Test invalid type."""
    # invalid type
    res = client_with_credentials.get(f"{prefix}/invalid", headers=h)
    assert res.status_code == 404


def test_names_forbidden(client, h, prefix, example_name, name_full_data):
    """Test invalid type."""
    # invalid type
    res = client.post(f"{prefix}", headers=h, data=json.dumps(name_full_data))
    assert res.status_code == 403

    res = client.put(
        f"{prefix}/{example_name.id}", headers=h, data=json.dumps(name_full_data)
    )
    assert res.status_code == 403

    res = client.delete(f"{prefix}/{example_name.id}")
    assert res.status_code == 403


def test_names_get(client_with_credentials, example_name, h, prefix):
    """Test the endpoint to retrieve a single item."""
    id_ = example_name.id

    res = client_with_credentials.get(f"{prefix}/{id_}", headers=h)
    assert res.status_code == 200
    assert res.json["id"] == id_
    # Test links
    assert res.json["links"] == {
        "self": f"https://127.0.0.1:5000/api/names/{example_name.id}"
    }


def test_names_search(client_with_credentials, example_name, h, prefix):
    """Test a successful search."""
    res = client_with_credentials.get(prefix, headers=h)

    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["sortBy"] == "name"


def test_names_resolve(client_with_credentials, example_name, h, prefix):
    res = client_with_credentials.get(f"{prefix}/orcid/0000-0001-8135-3489", headers=h)
    assert res.status_code == 200
    assert res.json["id"] == example_name.id

    res = client_with_credentials.get(f"{prefix}/orcid/0000-0002-5082-6404", headers=h)
    assert res.status_code == 404


def test_names_suggest_sort(client_with_credentials, example_multiple_names, h, prefix):
    """Test a successful search."""

    # With typo
    res = client_with_credentials.get(f"{prefix}?suggest=davisson", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["name"] == "Davidson, Niels John"

    # With accent
    res = client_with_credentials.get(f"{prefix}?suggest=dwayne", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["name"] == "Johnsœn, Dwäyne"

    res = client_with_credentials.get(
        f"{prefix}?suggest=Dw%C3%A4yne", headers=h
    )  # Dwäyne
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["name"] == "Johnsœn, Dwäyne"

    # With incomplete
    res = client_with_credentials.get(f"{prefix}?suggest=joh", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 3

    # With affiliation
    res = client_with_credentials.get(f"{prefix}?suggest=john%20wwe", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["name"] == "Cena, John"
    assert res.json["hits"]["hits"][0]["affiliations"][0]["name"] == "WWE"
