# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Affiliations JSONSchema tests."""

import pytest
from jsonschema.exceptions import ValidationError

from invenio_vocabularies.records.api import Vocabulary


@pytest.fixture(scope="function")
def vocabulary_json():
    """Returns the schema location."""
    return {
        "$schema": "local://vocabularies/vocabulary-v1.0.0.json",
        "description": {
            "en": "Test affiliation description",
            "es": "Descripcion de una afiliacion de test",
        },
        "icon": "test.png",
        "id": "voc-1",
        "pid": {"pk": 1, "status": "R", "pid_type": "vocid", "obj_type": "voc"},
        "props": {"example": "test"},
        "tags": ["one_tag", "two_tag"],
        "title": {"en": "Test affiliation", "es": "Afiliacion de test"},
        "type": {"id": "vocabulary", "pid_type": "vocid"},
    }


def validates(data):
    """Validates affiliation data."""
    Vocabulary(data).validate()

    return True


def fails(data):
    """Validates affiliation data."""
    pytest.raises(ValidationError, validates, data)
    return True


def test_valid_full(appctx, vocabulary_json):
    assert validates(vocabulary_json)


def test_valid_empty(appctx):
    # check there are no requirements at JSONSchema level
    data = {"$schema": "local://vocabularies/vocabulary-v1.0.0.json"}

    assert validates(data)


def test_fails_description(appctx, vocabulary_json):
    vocabulary_json["description"] = [
        "Test affiliation description",
        "Descripcion de una afiliacion de test",
    ]

    assert fails(vocabulary_json)

    vocabulary_json["description"] = [
        {"en": "Test affiliation description"},
        {"es": "Descripcion de una afiliacion de test"},
    ]

    assert fails(vocabulary_json)

    vocabulary_json["description"] = "Test affiliation description"

    assert fails(vocabulary_json)


def test_fails_icon(appctx, vocabulary_json):
    vocabulary_json["icon"] = 123
    assert fails(vocabulary_json)


def test_fails_props(appctx, vocabulary_json):
    vocabulary_json["props"] = {"key": 1234}
    assert fails(vocabulary_json)


def test_fails_tags(appctx, vocabulary_json):
    vocabulary_json["tags"] = "tag, tag too"

    assert fails(vocabulary_json)


def test_fails_title(appctx, vocabulary_json):
    vocabulary_json["title"] = ["Test affiliation", "Afiliacion de test"]

    assert fails(vocabulary_json)

    vocabulary_json["title"] = [
        {"en": "Test affiliation"},
        {"es": "Afiliacion de test"},
    ]

    assert fails(vocabulary_json)

    vocabulary_json["title"] = "Test affiliation"

    assert fails(vocabulary_json)
