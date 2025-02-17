# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the affiliation vocabulary resource."""

import json
from copy import deepcopy

import pytest

from invenio_vocabularies.contrib.affiliations.api import Affiliation


@pytest.fixture(scope="module")
def prefix():
    """API prefix."""
    return "affiliations"


@pytest.fixture()
def example_affiliation(
    app, db, search_clear, identity, service, affiliation_full_data
):
    """Example affiliation."""
    aff = service.create(identity, affiliation_full_data)
    Affiliation.index.refresh()  # Refresh the index

    return aff


def test_affiliations_invalid(client, h, prefix):
    """Test invalid type."""
    # invalid type
    res = client.get(f"{prefix}/invalid", headers=h)
    assert res.status_code == 404


def test_affiliations_forbidden(
    client, h, prefix, example_affiliation, affiliation_full_data
):
    """Test invalid type."""
    # invalid type
    affiliation_full_data_too = deepcopy(affiliation_full_data)
    affiliation_full_data_too["id"] = "other"
    res = client.post(
        f"{prefix}", headers=h, data=json.dumps(affiliation_full_data_too)
    )
    assert res.status_code == 403

    res = client.put(
        f"{prefix}/01ggx4157", headers=h, data=json.dumps(affiliation_full_data)
    )
    assert res.status_code == 403

    res = client.delete(f"{prefix}/01ggx4157")
    assert res.status_code == 403


def test_affiliations_get(client, example_affiliation, h, prefix):
    """Test the endpoint to retrieve a single item."""
    id_ = example_affiliation.id

    res = client.get(f"{prefix}/{id_}", headers=h)
    assert res.status_code == 200
    assert res.json["id"] == id_
    # Test links
    assert res.json["links"] == {
        "self": "https://127.0.0.1:5000/api/affiliations/01ggx4157"
    }


def test_affiliations_search(client, example_affiliation, h, prefix):
    """Test a successful search."""
    res = client.get(prefix, headers=h)

    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["sortBy"] == "name"


def _create_affiliations(service, identity):
    """Create dummy affiliations with similar names/acronyms/titles."""
    affiliations = [
        {
            "acronym": "CERN",
            "id": "cern",
            "name": "CERN",
            "title": {
                "en": "European Organization for Nuclear Research",
                "fr": "Conseil Européen pour la Recherche Nucléaire",
            },
        },
        {"acronym": "OTHER", "id": "other", "name": "OTHER", "title": {"en": "CERN"}},
        {
            "acronym": "CERT",
            "id": "cert",
            "name": "CERT",
            "title": {
                "en": "Computer Emergency Response Team",
                "fr": "Équipe d'Intervention d'Urgence Informatique",
            },
        },
        {
            "acronym": "NU",
            "id": "nu",
            "name": "Northwestern University",
            "title": {
                "en": "Northwestern University",
            },
            "identifiers": [{"identifier": "000e0be47", "scheme": "ror"}],
        },
        {
            "acronym": "NU",
            "id": "chnu",
            "name": "Northwestern University",
            "title": {
                "en": "Northwestern University",
            },
            "country_name": "Switzerland",
        },
        {
            "acronym": "LONG",
            "id": "LONG",
            "name": "!!! The Official Global Alliance of the Most Prestigious, Highly-Renowned, and Exceptionally Innovative Solutions for Business, Commerce, Trade, Finance, Investment, Corporate Services, Logistics, and International Market Expansion—Providing Cutting-Edge, World-Class, and State-of-the-Art Consulting, Advisory, and Strategic Development Services for Organizations of All Sizes, Sectors, and Industries Across the Globe, Inc. ???",
            "title": {
                "en": "!!! The Official Global Alliance of the Most Prestigious, Highly-Renowned, and Exceptionally Innovative Solutions for Business, Commerce, Trade, Finance, Investment, Corporate Services, Logistics, and International Market Expansion—Providing Cutting-Edge, World-Class, and State-of-the-Art Consulting, Advisory, and Strategic Development Services for Organizations of All Sizes, Sectors, and Industries Across the Globe, Inc. ???"
            },
        },
    ]
    for aff in affiliations:
        service.create(identity, aff)

    Affiliation.index.refresh()  # Refresh the index


def test_affiliations_prefix_search(
    app, db, search_clear, identity, service, client, h, prefix
):
    """Test a successful search."""
    _create_affiliations(service, identity)

    # Should show 2 results
    res = client.get(f"{prefix}?q=uni", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 2


def test_affiliations_suggest_sort(
    app, db, search_clear, identity, service, client, h, prefix
):
    """Test a successful search."""
    _create_affiliations(service, identity)

    # Should show 3 results, but id=cern as first due to acronym/name, CERT due to fuzziness
    res = client.get(f"{prefix}?suggest=CERN", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 3
    assert res.json["hits"]["hits"][0]["id"] == "cern"
    assert res.json["hits"]["hits"][1]["id"] == "cert"
    assert res.json["hits"]["hits"][2]["id"] == "other"

    # Should show 1 result, accent
    res = client.get(f"{prefix}?suggest=europeen", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["id"] == "cern"

    # Should show 2 results, but id=nu as first due to acronym
    res = client.get(f"{prefix}?suggest=NU", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 3
    assert res.json["hits"]["hits"][0]["id"] == "nu"
    assert res.json["hits"]["hits"][1]["id"] == "chnu"
    assert res.json["hits"]["hits"][2]["id"] == "cern"  # due to nucleaire

    # Should show a result and not error out for longer names
    res = client.get(
        f"{prefix}?suggest=The%20Official%20Global%20Alliance%20of%20the%20Most%20Prestigious%2C%20Highly-Renowned%2C%20and%20Exceptionally%20Innovative%20Solutions%20for%20Business%2C%20Commerce%2C%20Trade%2C%20Finance%2C%20Investment%2C%20Corporate%20Services%2C%20Logistics%2C%20and%20International%20Market%20Expansion%E2%80%94Providing%20Cutting-Edge%2C%20World-Class%2C%20and%20State-of-the-Art%20Consulting%2C%20Advisory%2C%20and%20Strategic%20Development%20Services%20for%20Organizations%20of%20All%20Sizes%2C%20Sectors%2C%20and%20Industries%20Across%20the%20Globe",
        headers=h,
    )
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["id"] == "LONG"

    # Search affiliations with ROR ID
    res = client.get(f"{prefix}?suggest=000e0be47", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["id"] == "nu"

    # Search affiliations with country
    res = client.get(f"{prefix}?suggest=Switzerland", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["id"] == "chnu"
