# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Resources layer tests."""


def test_endpoint_serialization(app, client, example_record):
    """Test that all the fields appear correctly"""

    res = client.get(
        "/vocabularies/languages", headers={"accept": "application/json"}
    )
    assert res.status_code == 200
    assert res.json["hits"]["hits"][0] == {
        "id": example_record.id,
        "title": "Test title",
        "type": 1,
        "description": "Test description",
        "icon": "icon-identifier",
    }
