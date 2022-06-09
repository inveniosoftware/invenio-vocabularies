# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
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
def example_affiliation(app, db, es_clear, identity, service, affiliation_full_data):
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
        f"{prefix}/cern", headers=h, data=json.dumps(affiliation_full_data)
    )
    assert res.status_code == 403

    res = client.delete(f"{prefix}/cern")
    assert res.status_code == 403


def test_affiliations_get(client, example_affiliation, h, prefix):
    """Test the endpoint to retrieve a single item."""
    id_ = example_affiliation.id

    res = client.get(f"{prefix}/{id_}", headers=h)
    assert res.status_code == 200
    assert res.json["id"] == id_
    # Test links
    assert res.json["links"] == {"self": "https://127.0.0.1:5000/api/affiliations/cern"}


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
        },
    ]
    for aff in affiliations:
        service.create(identity, aff)

    Affiliation.index.refresh()  # Refresh the index


def test_affiliations_suggest_sort(
    app, db, es_clear, identity, service, client, h, prefix
):
    """Test a successful search."""
    _create_affiliations(service, identity)

    # Should show 2 results, but id=cern as first due to acronym/name
    res = client.get(f"{prefix}?suggest=CERN", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 2
    assert res.json["hits"]["hits"][0]["id"] == "cern"
    assert res.json["hits"]["hits"][1]["id"] == "other"

    # Should show 1 result
    res = client.get(f"{prefix}?suggest=nucléaire", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["id"] == "cern"

    # Should show 2 results, but id=nu as first due to acronym/name
    res = client.get(f"{prefix}?suggest=nu", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 2
    assert res.json["hits"]["hits"][0]["id"] == "nu"
    assert res.json["hits"]["hits"][1]["id"] == "cern"  # due to nucleaire
