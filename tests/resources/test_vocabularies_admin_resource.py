# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""VocabulariesAdminResource tests."""

import pytest

from invenio_vocabularies.records.api import Vocabulary


#
# Fixtures
#
@pytest.fixture(scope="module")
def example_licenses_data():
    """Example data for records."""
    return [
        {
            "id": "cc-by",
            "title": {"en": "Creative Commons Attribution"},
            "type": "licenses",
        },
        {"id": "cc0", "title": {"en": "Creative Commons Zero"}, "type": "licenses"},
    ]


@pytest.fixture(scope="module")
def example_licenses_records(database, identity, service, example_licenses_data):
    """Create some example records."""
    service.create_type(identity, "licenses", "lic")
    records = [service.create(identity, data) for data in example_licenses_data]
    Vocabulary.index.refresh()
    return records


#
# Tests
#
def test_search(client, example_licenses_records, h):
    res = client.get("/vocabularies/", headers=h)

    assert 200 == res.status_code
    expected_links = {"self": "https://127.0.0.1:5000/api/vocabularies/?facets=%7B%7D"}
    assert expected_links == res.json["links"]
