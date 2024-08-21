# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Subject JSONSchema tests."""

import pytest
from jsonschema.exceptions import ValidationError

from invenio_vocabularies.contrib.subjects.api import Subject


@pytest.fixture(scope="module")
def schema():
    """Returns the schema location."""
    return "local://subjects/subject-v1.0.0.json"


def validates(data):
    """Validates subject data."""
    Subject(data).validate()
    return True


def fails(data):
    """Validates affiliation data."""
    pytest.raises(ValidationError, validates, data)
    return True


def test_valid_full(appctx, schema):
    data = {
        "$schema": schema,
        "title": {
            "en": "Dark Web",
            "de": "Darknet",
            "fr": "Réseaux anonymes (informatique)",
        },
        "id": "http://d-nb.info/gnd/1062531973",
        "pid": {"pk": 1, "status": "R", "pid_type": "subid", "obj_type": "sub"},
        "scheme": "GND",
        "synonyms": ["Deep Web"],
    }
    assert validates(data)


def test_valid_empty(appctx, schema):
    # check there are no requirements at JSONSchema level
    data = {"$schema": schema}

    assert validates(data)


def test_fails_scheme(appctx, schema):
    data = {"$schema": schema, "scheme": 1}

    assert fails(data)


def test_fails_name(appctx, schema):
    data = {"$schema": schema, "subject": 1}

    assert fails(data)
