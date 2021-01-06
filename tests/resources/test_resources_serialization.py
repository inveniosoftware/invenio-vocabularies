# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Resources layer tests."""


def test_endpoint_serialization(app, client, example_record):
    """Test that all the fields appear correctly."""

    res = client.get(
        "/vocabularies/languages", headers={"accept": "application/json"}
    )
    assert res.status_code == 200
    es_record = res.json["hits"]["hits"][0]
    assert es_record["id"] == example_record.id
    assert es_record["vocabulary_type_id"] == 1
    assert es_record["metadata"] == {
        "title": {"en": "Test title", "fr": "Titre test"},
        "description": {
            "en": "Test description",
            "de": "Textbeschreibung",
        },
        "icon": "icon-identifier",
        "props": {"key": "value"}
    }
