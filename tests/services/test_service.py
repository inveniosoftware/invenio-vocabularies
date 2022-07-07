# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the vocabulary service."""

import arrow
import pytest
from invenio_cache import current_cache
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
    return VocabularyType.create(id="licenses", pid_type="lic")


#
# Tests
#
def test_simple_flow(lang_type, lic_type, lang_data, service, identity):
    """Test a simple vocabulary service flow."""
    # Create it
    item = service.create(identity, lang_data)
    id_ = item.id

    assert item.id == lang_data["id"]
    for k, v in lang_data.items():
        assert item.data[k] == v

    # Read it
    read_item = service.read(identity, ("languages", "eng"))
    assert item.id == read_item.id
    assert item.data == read_item.data
    assert read_item.data["type"] == "languages"

    # Refresh index to make changes live.
    Vocabulary.index.refresh()

    # Search it
    res = service.search(identity, type="languages", q=f"id:{id_}", size=25, page=1)
    assert res.total == 1
    assert list(res.hits)[0] == read_item.data

    # Search another type
    res = service.search(identity, type="licenses", q=f"id:{id_}", size=25, page=1)
    assert res.total == 0

    # Update it
    data = read_item.data
    data["title"]["en"] = "New title"
    update_item = service.update(identity, ("languages", id_), data)
    assert item.id == update_item.id
    assert update_item["title"]["en"] == "New title"

    # Delete it
    assert service.delete(identity, ("languages", id_))

    # Refresh to make changes live
    Vocabulary.index.refresh()

    # Fail to retrieve it
    # - db
    pytest.raises(PIDDeletedError, service.read, identity, ("languages", id_))
    # - search
    res = service.search(identity, type="languages", q=f"id:{id_}", size=25, page=1)
    assert res.total == 0


def test_pid_already_registered(lang_type, lang_data, service, identity):
    """Recreating a record with same id should fail."""
    service.create(identity, lang_data)
    pytest.raises(PIDAlreadyExists, service.create, identity, lang_data)


def test_extra_fields(lang_data2, service, identity):
    """Extra fields in data should fail."""
    lang_data2["invalid"] = 1
    pytest.raises(ValidationError, service.create, identity, lang_data2)


def test_missing_or_invalid_type(lang_data2, service, identity):
    """A missing type should raise validation error."""
    # No type specified
    del lang_data2["type"]
    pytest.raises(ValidationError, service.create, identity, lang_data2)

    # Invalid value data types
    for val in [
        1,
        {"id": "languages"},
    ]:
        lang_data2["type"] = val
        pytest.raises(ValidationError, service.create, identity, lang_data2)

    # Non-existing type
    lang_data2["type"] = "invalid"
    pytest.raises(ValidationError, service.create, identity, lang_data2)


def test_update(lang_type, lang_data2, service, identity):
    """Removing keys should work."""
    lang_data2["id"] = "dan"
    item = service.create(identity, lang_data2)
    id_ = item.id

    data = item.data
    # Unset a subkey
    del data["title"]["en"]
    # Unset a top-level key
    del data["icon"]
    update_item = service.update(identity, ("languages", id_), data)
    # Ensure they really got cleared.
    assert "en" not in update_item.data["title"]
    assert "icon" not in update_item.data


def test_missing_or_invalid_type(lang_data2, service, identity):
    """Custom props should only accept strings."""
    # Invalid data types
    for v in [1, {"id": "test"}]:
        lang_data2["props"]["newkey"] = v
        pytest.raises(ValidationError, service.create, identity, lang_data2)


def test_read_all_no_cache(lang_type, lang_data_many, service, identity, cache):
    """read_all method should return all languages created in this scope."""
    items = service.read_all(identity, fields=["id"], type="languages", cache=False)
    assert set(lang_data_many).issubset(set([i["id"] for i in items]))
    cached = current_cache.get("id")
    assert not cached


def test_read_all_cache(lang_type, lang_data_many, service, identity, cache):
    """read_all method should return all languages created in this scope."""
    items = service.read_all(identity, fields=["id"], type="languages", cache=True)
    assert set(lang_data_many).issubset(set([i["id"] for i in items]))
    cached = current_cache.get("languages__id")
    assert cached is not None


def test_read_many(lang_type, lang_data_many, service, identity, search_clear):
    """read_many method should return all requested languages."""
    ids_ = ["fr", "tr", "es"]
    items = service.read_many(identity, type="languages", ids=ids_, fields=[])
    item_ids = [i.id for i in items._results]
    assert {"fr", "tr", "es"} == set(item_ids)


def test_indexed_at_query(app, db, service, identity, lang_type, lang_data):
    before = arrow.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")
    _ = service.create(identity, lang_data)
    now = arrow.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")
    Vocabulary.index.refresh()

    # there is previous to before
    res = service.search(
        identity,
        q=f"indexed_at:[* TO {before}]",
        type="languages",
    )
    assert res.total == 0

    # there is previous to now
    res = service.search(
        identity,
        q=f"indexed_at:[* TO {now}]",
        type="languages",
    )
    assert res.total == 1
