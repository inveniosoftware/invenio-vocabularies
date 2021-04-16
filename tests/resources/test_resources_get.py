# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Resources layer tests."""

import pytest

from invenio_vocabularies.records.api import Vocabulary


#
# Fixtures
#
@pytest.fixture()
def example_data():
    """Example data for records."""
    return [
        {'id': 'cc-by', 'title': {'en': 'Creative Commons Attribution'},
         'type': 'licenses'},
        {'id': 'cc0', 'title': {'en': 'Creative Commons Zero'},
         'type': 'licenses'},
    ]


@pytest.fixture()
def example_records(db, identity, service, example_data):
    """Create some example records."""
    service.create_type(identity, 'licenses', 'lic')
    records = []
    for data in example_data:
        records.append(service.create(identity, data))
    Vocabulary.index.refresh()
    return records


@pytest.fixture()
def prefix():
    """API prefix."""
    return '/vocabularies/licenses/'


#
# Tests
#
def test_get(client, example_records, h, prefix):
    """Test the endpoint to retrieve a single item."""
    id_ = example_records[0].id

    res = client.get(f'{prefix}{id_}', headers=h)
    assert res.status_code == 200
    assert res.json['id'] == id_
    # Test links
    assert res.json['links'] == {
        'self': 'https://127.0.0.1:5000/api/vocabularies/licenses/cc-by'
    }


def test_not_found(client, example_records, h, prefix):
    """Test not found."""
    id_ = example_records[0].id
    # invalid id
    res = client.get(f'{prefix}invalid-id', headers=h,)
    assert res.status_code == 404
    # invalid type (wrong type for pid)
    res = client.get(f'/vocabularies/invalid/{id_}', headers=h,)
    assert res.status_code == 404
    # trailing slash on search
    res = client.get(f'{prefix}/', headers=h,)
    assert res.status_code == 404
    # invalid type (not existing)
    res = client.get(f'/vocabularies/invalid', headers=h,)
    assert res.status_code == 404
