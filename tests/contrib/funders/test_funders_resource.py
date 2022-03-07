# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the funder vocabulary resource."""

import json
from copy import deepcopy

import pytest

from invenio_vocabularies.contrib.funders.api import Funder


@pytest.fixture(scope="module")
def prefix():
    """API prefix."""
    return "funders"


@pytest.fixture()
def example_funder(
    app, db, es_clear, identity, service, funder_full_data
):
    """Example funder."""
    fun = service.create(identity, funder_full_data)
    Funder.index.refresh()  # Refresh the index

    return fun


def test_funders_invalid(client, h, prefix):
    """Test invalid type."""
    # invalid type
    res = client.get(f"{prefix}/invalid", headers=h)
    assert res.status_code == 404


def test_funders_forbidden(
    client, h, prefix, example_funder, funder_full_data
):
    """Test invalid type."""
    # invalid type
    funder_full_data_too = deepcopy(funder_full_data)
    funder_full_data_too["id"] = "other"
    res = client.post(
        f"{prefix}", headers=h, data=json.dumps(funder_full_data_too))
    assert res.status_code == 403

    res = client.put(
        f"{prefix}/fund", headers=h, data=json.dumps(funder_full_data))
    assert res.status_code == 403

    res = client.delete(f"{prefix}/fund")
    assert res.status_code == 403


def test_funders_get(client, example_funder, h, prefix):
    """Test the endpoint to retrieve a single item."""
    id_ = example_funder.id

    res = client.get(f"{prefix}/{id_}", headers=h)
    assert res.status_code == 200
    assert res.json["id"] == id_
    # Test links
    assert res.json["links"] == {
        "self": "https://127.0.0.1:5000/api/funders/fund"
    }


def test_funders_search(client, example_funder, h, prefix):
    """Test a successful search."""
    res = client.get(prefix, headers=h)

    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["sortBy"] == "name"


def _create_funders(service, identity):
    """Create dummy funders with similar names/titles."""
    funders = [
        {
            "id": "cern",
            "name": "CERN",
            "country": "CH",
            "title": {
                "en": "European Organization for Nuclear Research",
                "fr": "Conseil Européen pour la Recherche Nucléaire"
            }
        },
        {
            "id": "other",
            "name": "OTHER",
            "country": "CH",
            "title": {
                "en": "CERN"
            }
        },
        {
            "id": "cert",
            "name": "CERT",
            "country": "CH",
            "title": {
                "en": "Computer Emergency Response Team",
                "fr": "Équipe d'Intervention d'Urgence Informatique"
            }
        },
        {
            "id": "nu",
            "name": "Northwestern University",
            "country": "US",
            "title": {
                "en": "Northwestern University",
            }
        }
    ]
    for fun in funders:
        service.create(identity, fun)

    Funder.index.refresh()  # Refresh the index


def test_funders_suggest_sort(client, h, identity, prefix, service):
    """Test a successful search."""
    _create_funders(service, identity)

    # Should show 3 results, but id=cern as first due to name
    res = client.get(f"{prefix}?suggest=CERN", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 2
    assert res.json["hits"]["hits"][0]["id"] == "cern"
    assert res.json["hits"]["hits"][1]["id"] == "other"

    # Should show 0 results since scheme is not searchable
    res = client.get(f"{prefix}?suggest=nucléaire", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1


def test_funders_delete(client_with_credentials, example_funder, h, prefix):
    """Test a successful delete."""
    id_ = example_funder.id
    res = client_with_credentials.delete(f"{prefix}/{id_}", headers=h)
    assert res.status_code == 204

    res = client_with_credentials.get(f"{prefix}/{id_}", headers=h)
    assert res.status_code == 410


def test_funders_update(
    client_with_credentials, example_funder, funder_full_data, h, prefix
):
    """Test a successful update."""
    id_ = example_funder.id
    new_name = "updated"
    funder_full_data["name"] = new_name
    res = client_with_credentials.put(
        f"{prefix}/fund", headers=h, data=json.dumps(funder_full_data))
    assert res.status_code == 200
    assert res.json["id"] == id_
    assert res.json["name"] == new_name


def test_funders_create(client_with_credentials, funder_full_data, h, prefix):
    """Tests a successful creation."""
    new_funder = {**funder_full_data}
    new_id = "new id"
    new_funder["id"] = new_id
    res = client_with_credentials.post(
        f"{prefix}", headers=h, data=json.dumps(new_funder))
    assert res.status_code == 201
    assert res.json["id"] == new_id
