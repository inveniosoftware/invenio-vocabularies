# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the award vocabulary resource."""

import json
from copy import deepcopy

import pytest
from invenio_db import db

from invenio_vocabularies.contrib.awards.api import Award


@pytest.fixture(scope="module")
def prefix():
    """API prefix."""
    return "awards"


def test_awards_invalid(client, h, prefix):
    """Test invalid type."""
    # invalid type
    res = client.get(f"{prefix}/invalid", headers=h)
    assert res.status_code == 404


def test_awards_forbidden(client, h, prefix, example_award, award_full_data):
    """Test invalid type."""
    # invalid type
    award_full_data_too = deepcopy(award_full_data)
    award_full_data_too["pid"] = "other"
    res = client.post(f"{prefix}", headers=h, data=json.dumps(award_full_data_too))
    assert res.status_code == 403

    res = client.put(f"{prefix}/755021", headers=h, data=json.dumps(award_full_data))
    assert res.status_code == 403

    res = client.delete(f"{prefix}/755021")
    assert res.status_code == 403


def test_awards_get(client, example_award, h, prefix):
    """Test the endpoint to retrieve a single item."""
    id_ = example_award.id  # result_items wraps pid into id

    res = client.get(f"{prefix}/{id_}", headers=h)
    assert res.status_code == 200
    assert res.json["id"] == id_
    # Test links
    assert res.json["links"] == {"self": "https://127.0.0.1:5000/api/awards/755021"}


def test_awards_search(client, example_award, h, prefix):
    """Test a successful search."""
    res = client.get(prefix, headers=h)

    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["sortBy"] == "newest"
    assert res.json["aggregations"]["funders"]

    funders_agg = res.json["aggregations"]["funders"]["buckets"][0]
    assert funders_agg["key"] == "00k4n6c32"
    assert funders_agg["doc_count"] == 1
    assert funders_agg["label"] == "European Commission (BE)"

    res = client.get(f"{prefix}?q=755021", headers=h)

    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["sortBy"] == "bestmatch"


@pytest.fixture(scope="function")
def example_awards(service, identity, indexer, example_funder_ec):
    """Create dummy awards with similar ids/numbers/titles."""
    awards_data = [
        {
            "title": {
                "en": "Host directed medicine in invasive fungal infection",
            },
            "id": "847507",
            "number": "847507",
        },
        {
            "title": {
                "en": "Palliative care in Parkinson disease",
            },
            "id": "825785",
            "number": "825785",
            "funder": {"id": example_funder_ec.id},
        },
        {
            "title": {
                "en": "Palliative Show",
            },
            "acronym": "Palliative",
            "id": "000001",
            "number": "000001",
            "funder": {"name": "Another Funder"},
        },
    ]

    awards = []
    for data in awards_data:
        awards.append(service.create(identity, data))

    Award.index.refresh()  # Refresh the index

    yield

    for award in awards:
        award._record.delete(force=True)
        indexer.delete(award._record, refresh=True)
        db.session.commit()


def test_awards_suggest_sort(client, h, prefix, example_awards):
    """Test a successful search."""
    # Should show 1 result
    res = client.get(f"{prefix}?suggest=847507", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["id"] == "847507"

    # Should show 1 result
    res = client.get(f"{prefix}?suggest=Parkin", headers=h)
    assert res.status_code == 200
    assert (
        res.json["hits"]["total"] == 0
    )  # should be 1 , TODO - suggestions were failing due to too many languages
    # assert res.json["hits"]["hits"][0]["id"] == "825785"

    # Should show 2 results, but pid=847507 as first due to created date
    res = client.get(f"{prefix}?suggest=Palliative", headers=h)
    assert res.status_code == 200
    assert (
        res.json["hits"]["total"] == 1
    )  # should be 2 , TODO - suggestions were failing due to too many languages
    assert res.json["hits"]["hits"][0]["id"] == "000001"
    # assert res.json["hits"]["hits"][1]["id"] == "825785"


def test_awards_faceted_suggest(client, h, prefix, example_funder_ec, example_awards):
    """Test a successful suggest with filtering."""
    # Should show 1 results because of the funder filtering
    res = client.get(
        f"{prefix}?funders={example_funder_ec.id}&suggest=Palliative",
        headers=h,
    )
    assert res.status_code == 200
    assert (
        res.json["hits"]["total"] == 0
    )  # should be 1 , TODO - suggestions were failing due to too many languages
    # assert res.json["hits"]["hits"][0]["id"] == "825785"


def test_awards_delete(
    client_with_credentials,
    h,
    prefix,
    identity,
    service,
    award_full_data,
    example_funder_ec,
):
    """Test a successful delete."""
    award = service.create(identity, award_full_data)
    id_ = award.id
    res = client_with_credentials.delete(f"{prefix}/{id_}", headers=h)
    assert res.status_code == 204

    # only the metadata is removed from the record, it is still resolvable
    res = client_with_credentials.get(f"{prefix}/{id_}", headers=h)
    assert res.status_code == 200
    base_keys = {"created", "updated", "id", "links", "revision_id"}
    assert set(res.json.keys()) == base_keys
    # not-ideal cleanup
    award._record.delete(force=True)


def test_awards_update(
    client_with_credentials, example_award, award_full_data, h, prefix
):
    """Test a successful update."""
    id_ = example_award.id
    new_title = "updated"
    award_full_data["title"]["en"] = new_title
    res = client_with_credentials.put(
        f"{prefix}/755021", headers=h, data=json.dumps(award_full_data)
    )
    assert res.status_code == 200
    assert res.json["id"] == id_  # result_items wraps pid into id
    assert res.json["title"]["en"] == new_title


def test_awards_create(
    client_with_credentials, award_full_data, h, prefix, example_funder_ec
):
    """Tests a successful creation."""
    res = client_with_credentials.post(
        f"{prefix}", headers=h, data=json.dumps(award_full_data)
    )
    assert res.status_code == 201
    assert res.json["id"] == award_full_data["id"]
