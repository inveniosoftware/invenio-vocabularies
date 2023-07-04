# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Awards JSONSchema tests."""

import pytest
from jsonschema.exceptions import ValidationError

from invenio_vocabularies.contrib.awards.api import Award


@pytest.fixture(scope="module")
def schema():
    """Returns the schema location."""
    return "local://awards/award-v1.0.0.json"


def validates(data):
    """Validates award data."""
    Award(data).validate()

    return True


def fails(data):
    """Validates award data."""
    pytest.raises(ValidationError, validates, data)
    return True


def test_valid_full(appctx, schema):
    data = {
        "$schema": schema,
        "identifiers": [
            {
                "identifier": "https://cordis.europa.eu/project/id/755021",
                "scheme": "url",
            }
        ],
        "title": {
            "en": "Personalised Treatment For Cystic Fibrosis Patients With \
                Ultra-rare CFTR Mutations (and beyond)"
        },
        "number": "755021",
        "funder": {"id": "ria", "name": "Research annd Innovation action"},
    }

    assert validates(data)


def test_valid_empty(appctx, schema):
    # check there are no requirements at JSONSchema level
    data = {"$schema": schema}

    assert validates(data)


# only number is defined by the award schema
# the rest are inherited and should be tested elsewhere


def test_fails_number(appctx, schema):
    data = {"$schema": schema, "number": 123}

    assert fails(data)
