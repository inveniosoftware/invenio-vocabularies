# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the vocabulary service."""

import pytest
from flask_principal import Identity, PermissionDenied
from invenio_access.permissions import any_user, system_identity

from invenio_vocabularies.records.api import Vocabulary


#
# Fixtures
#
@pytest.fixture()
def anyuser_idty():
    """Simple identity to interact with the service."""
    identity = Identity(1)
    identity.provides.add(any_user)
    return identity


#
# Tests
#
def test_permissions_readonly(anyuser_idty, lang_type, lang_data, service):
    """Read-only permission test.

    These tests will eventually need to be rewritten once a more advanced
    permission policy is put in place. Currently the permission policy only
    allows a system process to create/update/delete vocabularies.
    """
    # Create - only system allowed
    pytest.raises(PermissionDenied, service.create, anyuser_idty, lang_data)
    item = service.create(system_identity, lang_data)
    id_ = item.id

    # Read - both allowed
    item = service.read(anyuser_idty, ("languages", id_))
    item = service.read(system_identity, ("languages", id_))

    # Refresh index to make changes live.
    Vocabulary.index.refresh()

    # Search - both allowed
    res = service.search(anyuser_idty, type="languages", q=f"id:{id_}", size=25, page=1)
    assert res.total == 1
    res = service.search(
        system_identity, type="languages", q=f"id:{id_}", size=25, page=1
    )
    assert res.total == 1

    # Update - only system allowed
    data = item.data
    data["title"]["en"] = "New title"
    with pytest.raises(PermissionDenied):
        service.update(anyuser_idty, ("languages", id_), data)
    service.update(system_identity, ("languages", id_), data)

    # Delete - only system allowed
    with pytest.raises(PermissionDenied):
        service.delete(anyuser_idty, ("languages", id_))
    service.delete(system_identity, ("languages", id_))
