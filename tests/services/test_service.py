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
from invenio_pidstore.errors import PIDAlreadyExists, PIDDeletedError
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import IntegrityError

from invenio_vocabularies.records.api import Vocabulary, VocabularyType


#
# Fixtures
#
@pytest.fixture()
def lic_type(db):
    """Get a language vocabulary type."""
    return VocabularyType.create(id='licenses', pid_type='lic')


#
# Tests
#
def test_simple_flow(lang_type, lic_type, lang_data, service, identity):
    """Test a simple vocabulary service flow."""
    # Create it
    item = service.create(identity, lang_data)
    id_ = item.id

    assert item.id == lang_data['id']
    for k, v in lang_data.items():
        assert item.data[k] == v

    # Read it
    read_item = service.read(('languages', 'eng'), identity)
    assert item.id == read_item.id
    assert item.data == read_item.data
    assert read_item.data['type'] == 'languages'

    # Refresh index to make changes live.
    Vocabulary.index.refresh()

    # Search it
    res = service.search(
        identity, type='languages', q=f"id:{id_}", size=25, page=1)
    assert res.total == 1
    assert list(res.hits)[0] == read_item.data

    # Search another type
    res = service.search(
        identity, type='licenses', q=f"id:{id_}", size=25, page=1)
    assert res.total == 0

    # Update it
    data = read_item.data
    data['title']['en'] = 'New title'
    update_item = service.update(('languages', id_), identity, data)
    assert item.id == update_item.id
    assert update_item['title']['en'] == 'New title'

    # Delete it
    assert service.delete(('languages', id_), identity)

    # Refresh to make changes live
    Vocabulary.index.refresh()

    # Fail to retrieve it
    # - db
    pytest.raises(
        PIDDeletedError, service.read, ('languages', id_), identity)
    # - search
    res = service.search(
        identity, type='languages', q=f"id:{id_}", size=25, page=1)
    assert res.total == 0


def test_pid_already_registered(lang_type, lang_data, service, identity):
    """Recreating a record with same id should fail."""
    service.create(identity, lang_data)
    pytest.raises(PIDAlreadyExists, service.create, identity, lang_data)


def test_extra_fields(lang_data2, service, identity):
    """Extra fields in data should fail."""
    lang_data2['invalid'] = 1
    pytest.raises(ValidationError, service.create, identity, lang_data2)


def test_missing_or_invalid_type(lang_data2, service, identity):
    """A missing type should raise validation error."""
    # No type specified
    del lang_data2['type']
    pytest.raises(ValidationError, service.create, identity, lang_data2)

    # Invalid value data types
    for val in [1, {'id': 'languages'}, ]:
        lang_data2['type'] = val
        pytest.raises(
            ValidationError, service.create, identity, lang_data2)

    # Non-existing type
    lang_data2['type'] = 'invalid'
    pytest.raises(
            ValidationError, service.create, identity, lang_data2)


def test_update(lang_type, lang_data2, service, identity):
    """Removing keys should work."""
    lang_data2['id'] = 'dan'
    item = service.create(identity, lang_data2)
    id_ = item.id

    data = item.data
    # Unset a subkey
    del data['title']['en']
    # Unset a top-level key
    del data['icon']
    update_item = service.update(('languages', id_), identity, data)
    # Ensure they really got cleared.
    assert 'en' not in update_item.data['title']
    assert 'icon' not in update_item.data


def test_missing_or_invalid_type(lang_data2, service, identity):
    """Custom props should only accept strings."""
    # Invalid data types
    for v in [1, {'id': 'test'}]:
        lang_data2['props']['newkey'] = v
        pytest.raises(
            ValidationError, service.create, identity, lang_data2)
