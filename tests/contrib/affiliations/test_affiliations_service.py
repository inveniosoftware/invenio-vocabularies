# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the affiliation vocabulary service."""

import arrow
import pytest
from invenio_pidstore.errors import PIDAlreadyExists, PIDDeletedError
from marshmallow.exceptions import ValidationError

from invenio_vocabularies.contrib.affiliations.api import Affiliation


def test_simple_flow(app, db, service, identity, affiliation_full_data):
    """Test a simple vocabulary service flow."""
    # Service
    assert service.id == "affiliations"
    assert service.config.indexer_queue_name == "affiliations"

    # Create it
    item = service.create(identity, affiliation_full_data)
    id_ = item.id

    assert item.id == affiliation_full_data["id"]
    for k, v in affiliation_full_data.items():
        assert item.data[k] == v

    # Read it
    read_item = service.read(identity, "cern")
    assert item.id == read_item.id
    assert item.data == read_item.data

    # Refresh index to make changes live.
    Affiliation.index.refresh()

    # Search it
    res = service.search(identity, q=f"id:{id_}", size=25, page=1)
    assert res.total == 1
    assert list(res.hits)[0] == read_item.data

    # Update it
    data = read_item.data
    data["title"]["en"] = "New title"
    update_item = service.update(identity, id_, data)
    assert item.id == update_item.id
    assert update_item["title"]["en"] == "New title"

    # Delete it
    assert service.delete(identity, id_)

    # Refresh to make changes live
    Affiliation.index.refresh()

    # Fail to retrieve it
    # - db
    pytest.raises(PIDDeletedError, service.read, identity, id_)
    # - search
    res = service.search(identity, q=f"id:{id_}", size=25, page=1)
    assert res.total == 0


def test_pid_already_registered(
    app, db, es_clear, service, identity, affiliation_full_data
):
    """Recreating a record with same id should fail."""
    service.create(identity, affiliation_full_data)
    pytest.raises(PIDAlreadyExists, service.create, identity, affiliation_full_data)


def test_extra_fields(app, db, service, identity, affiliation_full_data):
    """Extra fields in data should fail."""
    affiliation_full_data["invalid"] = 1
    pytest.raises(ValidationError, service.create, identity, affiliation_full_data)


def test_indexed_at_query(app, db, service, identity, affiliation_full_data):
    before = arrow.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")
    _ = service.create(identity, affiliation_full_data)
    now = arrow.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")
    Affiliation.index.refresh()

    # there is previous to before
    res = service.search(identity, q=f"indexed_at:[* TO {before}]", size=25, page=1)
    assert res.total == 0

    # there is previous to now
    res = service.search(identity, q=f"indexed_at:[* TO {now}]", size=25, page=1)
    assert res.total == 1
