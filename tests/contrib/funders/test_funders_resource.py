# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the funder vocabulary resource."""

import json
from copy import deepcopy

import pytest
from invenio_db import db

from invenio_vocabularies.contrib.funders.api import Funder


@pytest.fixture(scope="module")
def prefix():
    """API prefix."""
    return "funders"


def test_funders_invalid(client, h, prefix):
    """Test invalid type."""
    # invalid type
    res = client.get(f"{prefix}/invalid", headers=h)
    assert res.status_code == 404


def test_funders_forbidden(client, h, prefix, example_funder, funder_full_data):
    """Test invalid type."""
    # invalid type
    funder_full_data_too = deepcopy(funder_full_data)
    funder_full_data_too["pid"] = "other"
    res = client.post(f"{prefix}", headers=h, data=json.dumps(funder_full_data_too))
    assert res.status_code == 403

    res = client.put(
        f"{prefix}/01ggx4157", headers=h, data=json.dumps(funder_full_data)
    )
    assert res.status_code == 403

    res = client.delete(f"{prefix}/01ggx4157")
    assert res.status_code == 403


def test_funders_get(client, example_funder, h, prefix):
    """Test the endpoint to retrieve a single item."""
    id_ = example_funder.id  # result_items wraps pid into id

    res = client.get(f"{prefix}/{id_}", headers=h)
    assert res.status_code == 200
    assert res.json["id"] == id_
    # Test links
    assert res.json["links"] == {"self": "https://127.0.0.1:5000/api/funders/01ggx4157"}


def test_funders_search(client, example_funder, h, prefix):
    """Test a successful search."""
    res = client.get(prefix, headers=h)

    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["sortBy"] == "name"


@pytest.fixture(scope="function")
def example_funders(service, identity, indexer):
    """Create dummy funders with similar names/titles."""
    funders_data = [
        {
            "id": "01ggx4157",
            "name": "CERN",
            "country": "CH",
            "title": {
                "en": "European Organization for Nuclear Research",
                "fr": "Conseil Européen pour la Recherche Nucléaire",
            },
            "identifiers": [{"identifier": "01ggx4157", "scheme": "ror"}],
        },
        {"id": "0aaaaaa11", "name": "OTHER", "country": "CH", "title": {"en": "CERN"}},
        {
            "id": "0aaaaaa22",
            "name": "CERT",
            "country": "CH",
            "title": {
                "en": "Computer Emergency Response Team",
                "fr": "Équipe d'Intervention d'Urgence Informatique",
            },
        },
        {
            "id": "000e0be47",
            "name": "Northwestern University",
            "country": "US",
            "title": {
                "en": "Northwestern University",
            },
        },
    ]
    funders = []
    for data in funders_data:
        funders.append(service.create(identity, data))
    Funder.index.refresh()  # Refresh the index

    yield

    for funder in funders:
        funder._record.delete(force=True)
        indexer.delete(funder._record, refresh=True)
        db.session.commit()


def test_funders_prefix_search(client, h, prefix, example_funders):
    """Test a successful search."""
    # Should show 1 result
    res = client.get(f"{prefix}?q=uni", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1


def test_funders_suggest_sort(client, h, prefix, example_funders):
    """Test a successful search."""

    # Should show 2 results, and id=cern as first due to name
    res = client.get(f"{prefix}?suggest=CERN", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 3
    assert res.json["hits"]["hits"][0]["name"] == "CERN"
    assert res.json["hits"]["hits"][1]["name"] == "CERT"
    # Matches lower, since title is boosted less
    assert res.json["hits"]["hits"][2]["name"] == "OTHER"
    assert res.json["hits"]["hits"][2]["title"]["en"] == "CERN"

    res = client.get(f"{prefix}?suggest=N%C3%B5rthw%C3%AAst", headers=h)  # Nõrthwêst
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["name"] == "Northwestern University"

    # Should show 0 results since scheme is not searchable
    res = client.get(f"{prefix}?suggest=nucl%C3%A9aire", headers=h)  # nucléaire
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 0

    # Search affiliations with identifier
    res = client.get(f"{prefix}?suggest=01ggx4157", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["name"] == "CERN"


def test_funders_delete(
    client_with_credentials, h, prefix, identity, service, funder_full_data
):
    """Test a successful delete."""
    funder = service.create(identity, funder_full_data)
    id_ = funder.id
    res = client_with_credentials.delete(f"{prefix}/{id_}", headers=h)
    assert res.status_code == 204

    # only the metadata is removed from the record, it is still resolvable
    res = client_with_credentials.get(f"{prefix}/{id_}", headers=h)
    assert res.status_code == 200
    base_keys = {"created", "updated", "id", "links", "revision_id"}
    assert set(res.json.keys()) == base_keys
    # not-ideal cleanup
    funder._record.delete(force=True)


def test_funders_update(
    client_with_credentials, example_funder, funder_full_data, h, prefix
):
    """Test a successful update."""
    id_ = example_funder.id
    new_name = "updated"
    funder_full_data["name"] = new_name
    res = client_with_credentials.put(
        f"{prefix}/01ggx4157", headers=h, data=json.dumps(funder_full_data)
    )
    assert res.status_code == 200
    assert res.json["id"] == id_  # result_items wraps pid into id
    assert res.json["name"] == new_name


def test_funders_create(client_with_credentials, funder_full_data, h, prefix):
    """Tests a successful creation."""
    res = client_with_credentials.post(
        f"{prefix}", headers=h, data=json.dumps(funder_full_data)
    )
    assert res.status_code == 201
    assert res.json["id"] == funder_full_data["id"]
