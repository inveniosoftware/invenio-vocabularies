# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Funders JSONSchema tests."""

import pytest
from jsonschema.exceptions import ValidationError

from invenio_vocabularies.contrib.funders.api import Funder


@pytest.fixture(scope="module")
def schema():
    """Returns the schema location."""
    return "local://funders/funder-v1.0.0.json"


def validates(data):
    """Validates funder data."""
    Funder(data).validate()

    return True


def fails(data):
    """Validates funder data."""
    pytest.raises(ValidationError, validates, data)
    return True


def test_valid_full(appctx, schema):
    data = {
        "$schema": schema,
        "name": "Test funder",
        "identifiers": [
            {
                "identifier": "0000000123456X",
                "scheme": "isni",
            },
            {
                "identifier": "grid.1234.5",
                "scheme": "grid",
            },
        ],
        "country": "CH",
    }

    assert validates(data)


def test_valid_empty(appctx, schema):
    # check there are no requirements at JSONSchema level
    data = {"$schema": schema}

    assert validates(data)


# name and country are defined by the funder schema
# the rest are inherited and should be tested elsewhere


def test_fails_name(appctx, schema):
    data = {"$schema": schema, "name": 1}

    assert fails(data)


def test_fails_country(appctx, schema):
    data = {"$schema": schema, "country": 1}

    assert fails(data)
