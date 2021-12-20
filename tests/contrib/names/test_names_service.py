# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the names vocabulary service."""

import pytest
from invenio_pidstore.errors import PIDDeletedError, PIDDoesNotExistError
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError

from invenio_vocabularies.contrib.names.api import Name


def test_simple_flow(
    app, service, identity, name_full_data, example_affiliation
):
    """Test a simple vocabulary service flow."""
    # Create it
    item = service.create(identity, name_full_data)
    id_ = item.id

    for k, v in name_full_data.items():
        assert item.data[k] == v

    # Read it
    read_item = service.read(identity, id_)
    assert item.id == read_item.id
    assert item.data == read_item.data

    # Refresh index to make changes live.
    Name.index.refresh()

    # Search it
    res = service.search(
        identity, q=f"id:{id_}", size=25, page=1)
    assert res.total == 1
    assert list(res.hits)[0] == read_item.data

    # Update it
    data = read_item.data
    data["given_name"] = "Jane"
    update_item = service.update(identity, id_, data)
    assert item.id == update_item.id
    assert update_item['given_name'] == 'Jane'
    assert update_item['name'] == "Doe, Jane"  # automatic update

    # Delete it
    assert service.delete(identity, id_)

    # Refresh to make changes live
    Name.index.refresh()

    # Fail to retrieve it
    # - db
    pytest.raises(PIDDeletedError, service.read, identity, id_)
    # - search
    res = service.search(identity, q=f"id:{id_}", size=25, page=1)
    assert res.total == 0


def test_extra_fields(app, service, identity, name_full_data):
    """Extra fields in data should fail."""
    name_full_data['invalid'] = 1
    pytest.raises(ValidationError, service.create, identity, name_full_data)


def test_identifier_resolution(
    app, service, identity, name_full_data, example_affiliation
):
    # Create it
    item = service.create(identity, name_full_data)
    id_ = item.id

    Name.index.refresh()
    resolved = service.resolve(
        identity,
        id_="0000-0001-8135-3489",
        id_type="orcid"
    )
    assert resolved.id == id_

    # non-existent orcid
    pytest.raises(
        PIDDoesNotExistError,
        service.resolve,
        identity,
        "0000-0002-5082-6404",
        "orcid"
    )

    # non-existent scheme
    pytest.raises(
        PIDDoesNotExistError,
        service.resolve,
        identity,
        "0000-0001-8135-3489",
        "invalid"
    )
