# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the names vocabulary permissions."""

import pytest
from flask_principal import Identity
from invenio_access.permissions import any_user, authenticated_user
from invenio_records_resources.services.errors import (
    PermissionDeniedError,
    RecordPermissionDeniedError,
)


#
# Fixtures
#
@pytest.fixture()
def anyuser_idty():
    """Simple identity to interact with the service."""
    identity = Identity(1)
    identity.provides.add(any_user)
    return identity


@pytest.fixture()
def authenticated_user_idty():
    """Authenticated identity to interact with the service."""
    identity = Identity(2)
    identity.provides.add(authenticated_user)
    return identity


def test_non_searchable_tag(
    app,
    service,
    identity,
    non_searchable_name_data,
    anyuser_idty,
    authenticated_user_idty,
    example_affiliation,
    superuser_identity,
    indexer,
):
    """Test that unlisted tags are not returned in search results."""
    # Service
    assert service.id == "names"
    assert service.config.indexer_queue_name == "names"
    # Create it
    item = service.create(identity, non_searchable_name_data)
    id_ = item.id

    # Index document in ES
    assert indexer.refresh()

    with pytest.raises(PermissionDeniedError):
        res = service.search(anyuser_idty, type="names", q=f"id:{id_}", size=25, page=1)

    # Search - only searchable values should be returned
    res = service.search(
        authenticated_user_idty, type="names", q=f"id:{id_}", size=25, page=1
    )
    assert res.total == 0
    # Anyuser should not be able to read the record
    with pytest.raises(RecordPermissionDeniedError):
        service.read(anyuser_idty, id_)

    # Authenticated user should not be able to read the record
    with pytest.raises(RecordPermissionDeniedError):
        test = service.read(authenticated_user_idty, id_)

    # Admins should be able to see the unlisted tags
    res = service.search(
        superuser_identity, type="names", q=f"id:{id_}", size=25, page=1
    )
    assert res.total == 1

    item = service.read(superuser_identity, id_)

    assert item["id"] == id_
