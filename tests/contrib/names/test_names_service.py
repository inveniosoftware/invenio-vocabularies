# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the names vocabulary service."""

from copy import deepcopy

import arrow
import pytest
from invenio_pidstore.errors import PIDDoesNotExistError
from marshmallow.exceptions import ValidationError

from invenio_vocabularies.contrib.names.api import Name


def test_simple_flow(app, service, identity, name_full_data, example_affiliation):
    """Test a simple vocabulary service flow."""
    # Service
    assert service.id == "names"
    assert service.config.indexer_queue_name == "names"

    # Create it
    item = service.create(identity, name_full_data)

    id_ = item.id

    # add dereferenced values
    expected_data = deepcopy(name_full_data)
    expected_data["affiliations"][0][
        "name"
    ] = "European Organization for Nuclear Research"

    for k, v in expected_data.items():
        assert item.data[k] == v

    # Read it
    read_item = service.read(identity, id_)
    assert item.id == read_item.id
    assert item.data == read_item.data

    # Refresh index to make changes live.
    Name.index.refresh()

    # Search it
    res = service.search(identity, q=f"id:{id_}", size=25, page=1)
    assert res.total == 1
    assert list(res.hits)[0] == read_item.data

    # Update it
    data = read_item.data
    data["given_name"] = "Jane"
    update_item = service.update(identity, id_, data)
    assert item.id == update_item.id
    assert update_item["given_name"] == "Jane"
    assert update_item["name"] == "Doe, Jane"  # automatic update

    # Delete it
    assert service.delete(identity, id_)

    # Refresh to make changes live
    Name.index.refresh()

    # Fail to retrieve it
    # - db
    # only the metadata is removed from the record, it is still resolvable
    base_keys = {"created", "updated", "id", "links", "revision_id", "internal_id"}
    deleted_rec = service.read(identity, id_).to_dict()
    assert set(deleted_rec.keys()) == base_keys
    # - search
    res = service.search(identity, q=f"id:{id_}", size=25, page=1)
    assert res.total == 0


def test_extra_fields(app, service, identity, name_full_data):
    """Extra fields in data should fail."""
    name_full_data["invalid"] = 1
    pytest.raises(ValidationError, service.create, identity, name_full_data)


def test_identifier_resolution(
    app, search_clear, service, identity, name_full_data, example_affiliation
):
    # Create it
    item = service.create(identity, name_full_data)
    id_ = item.id

    Name.index.refresh()
    resolved = service.resolve(identity, id_="0000-0001-8135-3489", id_type="orcid")
    assert resolved.id == id_

    # non-existent orcid
    pytest.raises(
        PIDDoesNotExistError, service.resolve, identity, "0000-0002-5082-6404", "orcid"
    )

    # non-existent scheme
    pytest.raises(
        PIDDoesNotExistError,
        service.resolve,
        identity,
        "0000-0001-8135-3489",
        "invalid",
    )


def test_names_dereferenced(app, search_clear, service, identity, example_affiliation):
    """Extra fields in data should fail."""
    expected_aff = {"id": "cern", "name": "European Organization for Nuclear Research"}

    name_data = {
        "id": "0000-0001-8135-3489",
        "name": "Doe, John",
        "affiliations": [{"id": "cern"}],
    }

    # data is not dereferenced
    assert not name_data["affiliations"][0].get("name")
    # create it
    item = service.create(identity, name_data)
    Name.index.refresh()
    id_ = item.id
    assert item["affiliations"][0] == expected_aff

    # read it
    read_item = service.read(identity, id_)
    assert read_item["affiliations"][0] == expected_aff

    # search it
    res = service.search(identity, q=f"id:{id_}", size=25, page=1)
    assert res.total == 1
    assert list(res.hits)[0]["affiliations"][0] == expected_aff


def test_indexed_at_query(
    app, db, service, identity, name_full_data, example_affiliation
):
    before = arrow.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")
    _ = service.create(identity, name_full_data)
    now = arrow.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")
    Name.index.refresh()

    # there is previous to before
    res = service.search(identity, q=f"indexed_at:[* TO {before}]", size=25, page=1)
    assert res.total == 0

    # there is previous to now
    res = service.search(identity, q=f"indexed_at:[* TO {now}]", size=25, page=1)
    assert res.total == 1
