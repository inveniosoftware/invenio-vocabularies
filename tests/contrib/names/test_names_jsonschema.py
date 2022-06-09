# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names JSONSchema tests."""

import pytest
from jsonschema.exceptions import ValidationError

from invenio_vocabularies.contrib.names.api import Name


@pytest.fixture(scope="module")
def schema():
    """Returns the schema location."""
    return "local://names/name-v1.0.0.json"


def validates(data):
    """Validates names data."""
    Name(data).validate()

    return True


def fails(data):
    """Validates names data."""
    pytest.raises(ValidationError, validates, data)
    return True


def test_valid_full(appctx, schema):
    data = {
        "$schema": schema,
        "name": "Doe, John",
        "given_name": "John",
        "family_name": "Doe",
        "identifiers": [{"identifier": "0000-0001-8135-3489", "scheme": "orcid"}],
        "affiliations": [{"id": "cern"}, {"name": "CustomORG"}],
    }
    assert validates(data)


def test_valid_empty(appctx, schema):
    # check there are no requirements at JSONSchema level
    data = {"$schema": schema}

    assert validates(data)


# only acronym and name are defined by the affiliation schema
# the rest are inherited and should be tested elsewhere


def test_fails_name_identifiers(appctx, schema):
    # string
    data = {"$schema": schema, "identifiers": "0000-0001-8135-3489"}

    assert fails(data)

    # dict
    data = {
        "$schema": schema,
        "identifiers": {"identifier": "0000-0001-8135-3489", "scheme": "orcid"},
    }

    assert fails(data)


def test_fails_name_affiliations(appctx, schema):
    # string, comma separated list
    data = {"$schema": schema, "affiliations": "cern, CustomORG"}

    assert fails(data)

    # dict
    data = {"$schema": schema, "affiliations": {"id": "cern", "name": "CustomORG"}}

    assert fails(data)
