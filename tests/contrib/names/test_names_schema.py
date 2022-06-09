# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names Marshmallow schema tests."""

import pytest
from marshmallow import ValidationError

from invenio_vocabularies.contrib.names.schema import NameSchema


def test_valid_full(app, name_full_data):
    loaded = NameSchema().load(name_full_data)
    assert name_full_data == loaded


def test_valid_minimal(app):
    data = {
        "name": "Doe, John",
    }
    loaded = NameSchema().load(data)
    assert data == loaded

    data = {"family_name": "Doe", "given_name": "John"}
    loaded = NameSchema().load(data)
    data["name"] = "Doe, John"  # it will be calculated and included
    assert data == loaded


def test_invalid_no_names(app):
    # no name
    invalid = {
        "identifiers": [{"identifier": "0000-0001-8135-3489", "scheme": "orcid"}],
        "affiliations": [{"id": "cern"}, {"name": "CustomORG"}],
    }
    with pytest.raises(ValidationError):
        data = NameSchema().load(invalid)

    # only given name
    invalid["given_name"] = ("John",)

    with pytest.raises(ValidationError):
        data = NameSchema().load(invalid)

    # only family name
    invalid["family_name"] = ("Doe",)
    invalid.pop("given_name")

    with pytest.raises(ValidationError):
        data = NameSchema().load(invalid)
