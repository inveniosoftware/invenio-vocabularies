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

from invenio_vocabularies.contrib.affiliations.api import Affiliation


@pytest.fixture(scope="module")
def schema():
    """Returns the schema location."""
    return "local://affiliations/affiliation-v1.0.0.json"


def validates(data):
    """Validates affiliation data."""
    Affiliation(data).validate()

    return True


def fails(data):
    """Validates affiliation data."""
    pytest.raises(ValidationError, validates, data)
    return True


def test_valid_full(appctx, schema):
    data = {
        "$schema": schema,
        "acronym": "TEST",
        "identifiers": [{"identifier": "03yrm5c26", "scheme": "ror"}],
        "name": "Test affiliation",
        "title": {"en": "Test affiliation", "es": "Afiliacion de test"},
    }

    assert validates(data)


def test_valid_empty(appctx, schema):
    # check there are no requirements at JSONSchema level
    data = {"$schema": schema}

    assert validates(data)


# only acronym and name are defined by the affiliation schema
# the rest are inherited and should be tested elsewhere


def test_fails_acronym(appctx, schema):
    data = {"$schema": schema, "acronym": 1}

    assert fails(data)


def test_fails_name(appctx, schema):
    data = {"$schema": schema, "name": 1}

    assert fails(data)
