# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the funder vocabulary service."""

import pytest
from invenio_pidstore.errors import PIDAlreadyExists, PIDDeletedError
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError

from invenio_vocabularies.contrib.funders.api import Funder


def test_simple_flow(app, db, service, identity, funder_full_data):
    """Test a simple vocabulary service flow."""
    # Create it
    item = service.create(identity, funder_full_data)
    id_ = item.id

    assert item.id == funder_full_data['id']
    for k, v in funder_full_data.items():
        assert item.data[k] == v

    # Read it
    read_item = service.read(identity, 'fund')

    assert item.id == read_item.id
    assert item.data == read_item.data

    # Refresh index to make changes live.
    Funder.index.refresh()

    # Search it
    res = service.search(
        identity, q=f"id:{id_}", size=25, page=1)
    assert res.total == 1
    assert list(res.hits)[0] == read_item.data

    # Update its country
    data = read_item.data
    data['country'] = 'New country'
    update_item = service.update(identity, id_, data)
    assert item.id == update_item.id
    assert update_item['country'] == 'New country'

    # Update its title
    data = read_item.data
    data['title']['en'] = 'New title'
    update_item = service.update(identity, id_, data)
    assert item.id == update_item.id
    assert update_item['title']['en'] == 'New title'

    # Delete it
    assert service.delete(identity, id_)

    # Refresh to make changes live
    Funder.index.refresh()

    # Fail to retrieve it
    # - db
    pytest.raises(PIDDeletedError, service.read, identity, id_)
    # - search
    res = service.search(
        identity, q=f"id:{id_}", size=25, page=1)
    assert res.total == 0


def test_pid_already_registered(
    app, db, service, identity, funder_full_data
):
    """Recreating a record with same id should fail."""
    service.create(identity, funder_full_data)
    pytest.raises(
        PIDAlreadyExists, service.create, identity, funder_full_data)


def test_extra_fields(app, db, service, identity, funder_full_data):
    """Extra fields in data should fail."""
    funder_full_data['invalid'] = 1
    pytest.raises(
        ValidationError, service.create, identity, funder_full_data)
