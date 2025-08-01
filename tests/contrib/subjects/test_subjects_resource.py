# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2025 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the subject vocabulary resource."""

from copy import deepcopy

import pytest

from invenio_vocabularies.contrib.subjects.api import Subject


@pytest.fixture(scope="module")
def prefix():
    """API prefix."""
    return "subjects"


@pytest.fixture()
def example_subject(app, db, search_clear, identity, service, subject_full_data):
    """Example subject."""
    subject = service.create(identity, subject_full_data)
    Subject.index.refresh()  # Refresh the index
    return subject


def test_get(client, h, prefix, example_subject):
    """Test the endpoint to retrieve a single item."""
    id_ = example_subject.id

    res = client.get(f"{prefix}/{id_}", headers=h)
    assert res.status_code == 200
    assert res.json["id"] == id_
    # links are encoded which seems weird
    assert res.json["links"] == {
        "self": "https://127.0.0.1:5000/api/subjects/http%3A%2F%2Fd-nb.info%2Fgnd%2F1062531973"  # noqa
    }
    # but they should still resolve
    i = res.json["links"]["self"].find("subjects")
    link = res.json["links"]["self"][i:]
    res = client.get(link, headers=h)
    assert res.status_code == 200


def test_get_invalid(client, h, prefix):
    res = client.get(f"{prefix}/invalid", headers=h)
    assert res.status_code == 404


def test_forbidden_endpoints(client, h, prefix, example_subject, subject_full_data):
    # POST
    subject_full_data_too = deepcopy(subject_full_data)
    subject_full_data_too["id"] = "other"
    res = client.post(f"{prefix}", headers=h, json=subject_full_data_too)
    assert res.status_code == 403

    # PUT
    id_ = example_subject.id
    res = client.put(f"{prefix}/{id_}", headers=h, json=subject_full_data)
    assert res.status_code == 403

    # DELETE
    res = client.delete(f"{prefix}/{id_}")
    assert res.status_code == 403


def test_search(client, h, prefix, example_subject):
    """Test a successful search."""
    res = client.get(f"{prefix}", headers=h)

    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["sortBy"] == "subject"


@pytest.fixture()
def example_subjects(app, db, search_clear, identity, service):
    subjects = [
        {
            "id": "other-1",
            "scheme": "Other",
            "title": {
                "en": "Abdomen",
            },
            "subject": "Abdomen",
        },
        {
            "id": "https://id.nlm.nih.gov/mesh/D000001",
            "scheme": "MeSH",
            "title": {
                "en": "Calcimycin",
            },
            "subject": "Calcimycin",
        },
        {
            "id": "https://id.nlm.nih.gov/mesh/D000005",
            "scheme": "MeSH",
            "title": {
                "en": "Abdomen",
            },
            "subject": "Abdomen",
        },
        {
            "id": "https://id.nlm.nih.gov/mesh/D000006",
            "scheme": "MeSH",
            "title": {
                "en": "Abdomen, Acute",
            },
            "subject": "Abdomen, Acute",
        },
        {
            "id": "yet-another-954514",
            "scheme": "Other2",
            "title": {
                "en": "Abdomen",
            },
            "subject": "Abdomen",
        },
    ]
    records = [service.create(identity, s) for s in subjects]
    Subject.index.refresh()  # Refresh the index
    return records


def test_suggest(client, h, prefix, example_subjects):
    """Test the subjects query parser."""
    # Full word
    res = client.get(f"{prefix}?suggest=abdomen", headers=h)
    assert res.json["hits"]["total"] == 4
    # The less specific text appears at the end of the list
    assert res.json["hits"]["hits"][3]["subject"] == "Abdomen, Acute"

    # Incomplete word -> finds the same results
    res = client.get(f"{prefix}?suggest=abdo", headers=h)
    assert res.json["hits"]["total"] == 4

    # Multiple words -> narrows down the results
    res = client.get(f"{prefix}?suggest=abdomen%20acute", headers=h)
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["subject"] == "Abdomen, Acute"

    # Multiple words with incomplete last word -> still finds the same result
    res = client.get(f"{prefix}?suggest=abdomen%20acu", headers=h)
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["subject"] == "Abdomen, Acute"

    # Multiple words with incomplete last word in other order -> still finds the same result
    res = client.get(f"{prefix}?suggest=acute%20abdo", headers=h)
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["subject"] == "Abdomen, Acute"

    # Single filter
    res = client.get(f"{prefix}?suggest=MeSH:abdo", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 2

    # Multiple filters
    res = client.get(f"{prefix}?suggest=MeSH,Other:abdo", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 3

    # Ignore non existing filter
    res = client.get(f"{prefix}?suggest=MeSH,Foo:abdo", headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 2
