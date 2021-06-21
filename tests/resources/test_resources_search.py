# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""REST API search tests."""

import pytest

from invenio_vocabularies.records.api import Vocabulary


#
# Fixtures
#
@pytest.fixture(scope='module')
def example_data():
    """Example data for records."""
    return [
        {'id': 'text', 'title': {'en': 'Text'}, 'type': 'resourcetypes'},
        {'id': 'data', 'title': {'en': 'Data'}, 'type': 'resourcetypes',
         'tags': ['recommended']},
    ]


@pytest.fixture(scope='module')
def example_records(database, identity, service, example_data):
    """Create some example records."""
    service.create_type(identity, 'resourcetypes', 'rt')
    records = []
    for data in example_data:
        records.append(service.create(identity, data))
    Vocabulary.index.refresh()
    return records


@pytest.fixture()
def prefix():
    """API prefix."""
    return '/vocabularies/resourcetypes'


#
# Tests
#
def test_invalid_type(app, client, h):
    """Test invalid type."""
    # invalid type
    res = client.get('/vocabularies/invalid', headers=h)
    assert res.status_code == 404
    # trailing slash
    res = client.get('/vocabularies/invalid/', headers=h)
    assert res.status_code == 404


def test_type_as_query_arg(app, lang_type, example_records, client, h, prefix):
    """Test passing an invalid query parameter."""
    # Ensure we cannot pass invalid query parameters
    res = client.get(f'{prefix}?invalid=test', headers=h)
    assert res.status_code == 200
    assert 'invalid' not in res.json['links']['self']

    # It should not be possible to pass 'type' in query args (because it's in
    # the URL route instead)
    res = client.get(f'{prefix}?type={lang_type.id}', headers=h)
    assert res.status_code == 200
    assert lang_type.id not in res.json['links']['self']
    assert 'type=' not in res.json['links']['self']
    assert 'resourcetypes' in res.json['links']['self']


def test_search(client, example_records, h, prefix):
    """Test a successful search."""
    res = client.get(prefix, headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 2
    assert res.json['sortBy'] == 'title'


def test_query_q(client, example_records, h, prefix):
    """Test a successful search."""
    # Test query (q=)
    res = client.get(f'{prefix}?q=title.en:text', headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json['sortBy'] == 'bestmatch'

    # Test sort
    res = client.get(f'{prefix}?q=*&sort=bestmatch', headers=h)
    assert res.status_code == 200
    assert res.json['sortBy'] == 'bestmatch'

    # Test size
    res = client.get(f'{prefix}?size=1&page=1', headers=h)
    assert res.status_code == 200
    assert res.json['hits']['total'] == 2
    assert len(res.json['hits']['hits']) == 1
    assert 'next' in res.json['links']


def test_tags_filter(client, example_records, h, prefix):
    """Test filter on tags."""
    # Test query (q=)
    res = client.get(f'{prefix}?tags=recommended', headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1


@pytest.fixture(scope='module')
def example_subjects(database, identity, service):
    """Example subjects for records."""
    service.create_type(identity, 'subjects', 'sub')
    service.create_subtype(
        identity, 'mesh', 'subjects',
        label="MeSH", prefix_url="http://id.nlm.nih.gov/mesh/"
    )
    subjects = [
        {
            'id': 'XYZ1234',
            'title': {'en': 'Abdoctor'},
            'type': 'subjects',
            'tags': ['my-custom-subject']
        },
        {
            "id": "D000001",
            'title': {'en': 'Calcimycin'},
            'type': 'subjects',
            'tags': ['mesh']
        },
        {
            'id': 'D000005',
            'title': {'en': 'Abdomen'},
            'type': 'subjects',
            'tags': ['mesh']
        },
        {
            'id': 'D000006',
            'title': {'en': 'Abdomen, Acute'},
            'type': 'subjects',
            'tags': ['mesh']
        },
        {
            'id': 'D000007',
            'title': {'en': 'Abdominal Injuries'},
            'type': 'subjects',
            'tags': ['mesh']
        },
        {
            'id': '954514',
            'title': {'en': 'Abdominal thrust maneuver'},
            'type': 'subjects',
            'tags': ['fast']
        },
    ]
    records = [service.create(identity, s) for s in subjects]
    Vocabulary.index.refresh()
    return records


def test_query_suggest(client, example_subjects, h):
    """Test FilteredSuggestParam."""
    prefix = '/vocabularies/subjects'

    # No prefix
    res = client.get(f'{prefix}?suggest=abdo', headers=h)
    assert res.json["hits"]["total"] == 5

    # Single prefix
    res = client.get(f'{prefix}?suggest=mesh:abdo', headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 3, res.json

    # Multiple prefixes
    res = client.get(f'{prefix}?suggest=mesh,fast:abdo', headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 4, res.json

    # Ignore non existing prefix
    res = client.get(f'{prefix}?suggest=mesh,foo:abdo', headers=h)
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 3, res.json
