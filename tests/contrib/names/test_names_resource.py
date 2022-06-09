# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the name vocabulary resource."""

import json
from copy import deepcopy

import pytest

from invenio_vocabularies.contrib.names.api import Name


@pytest.fixture(scope="module")
def prefix():
    """API prefix."""
    return "names"


@pytest.fixture()
def example_name(
    app, db, es_clear, identity, service, name_full_data, example_affiliation
):
    """Example affiliation."""
    name = service.create(identity, name_full_data)
    Name.index.refresh()  # Refresh the index

    return name


def test_names_invalid(client, h, prefix):
    """Test invalid type."""
    # invalid type
    res = client.get(f"{prefix}/invalid", headers=h)
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


def test_names_get(client, example_name, h, prefix):
    """Test the endpoint to retrieve a single item."""
    id_ = example_name.id

    res = client.get(f"{prefix}/{id_}", headers=h)
    assert res.status_code == 200
    assert res.json["id"] == id_
    # Test links
    assert res.json["links"] == {
        "self": f"https://127.0.0.1:5000/api/names/{example_name.id}"
    }


def test_names_search(client, example_name, h, prefix):
    """Test a successful search."""
    res = client.get(prefix, headers=h)

    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["sortBy"] == "name"


def test_names_resolve(client, example_name, h, prefix):
    res = client.get(f"{prefix}/orcid/0000-0001-8135-3489", headers=h)
    assert res.status_code == 200
    assert res.json["id"] == example_name.id

    res = client.get(f"{prefix}/orcid/0000-0002-5082-6404", headers=h)
    assert res.status_code == 404
