# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test funder schema."""

import pytest
from marshmallow import ValidationError

from invenio_vocabularies.contrib.funders.schema import (
    FunderRelationSchema,
    FunderSchema,
)


def test_valid_full(app, funder_full_data):
    loaded = FunderSchema().load(funder_full_data)
    funder_full_data["pid"] = funder_full_data.pop("id")
    assert funder_full_data == loaded


def test_valid_minimal(app):
    data = {
        "id": "01ggx4157",
        "name": "Test funder",
    }
    assert {
        "pid": "01ggx4157",
        "name": "Test funder",
    } == FunderSchema().load(data)


def test_invalid_no_name():
    invalid_no_name = {
        "id": "01ggx4157",
        "identifiers": [
            {
                "identifier": "000000012156142X",
                "scheme": "isni",
            },
            {
                "identifier": "grid.9132.9",
                "scheme": "grid",
            },
        ],
        "title": {
            "en": "European Organization for Nuclear Research",
            "fr": "Organisation européenne pour la recherche nucléaire",
        },
        "country": "CH",
    }
    with pytest.raises(ValidationError):
        data = FunderSchema().load(invalid_no_name)


def test_invalid_empty(app):
    data = {
        "id": "01ggx4157",
        "name": "",
    }
    with pytest.raises(ValidationError):
        data = FunderSchema().load(data)

    data = {
        "id": "",
        "name": "Test funder",
    }
    with pytest.raises(ValidationError):
        data = FunderSchema().load(data)


def test_invalid_empty_funder():
    invalid_empty = {}
    with pytest.raises(ValidationError):
        data = FunderSchema().load(invalid_empty)


def test_invalid_country():
    invalid_country = {"id": "01ggx4157", "name": "Test funder", "country": 1}
    with pytest.raises(ValidationError):
        data = FunderSchema().load(invalid_country)


#
# FunderRelationSchema
#


def test_valid_id():
    valid_id = {
        "id": "test",
    }
    assert valid_id == FunderRelationSchema().load(valid_id)


def test_valid_name():
    valid_name = {"name": "Funder One"}
    assert valid_name == FunderRelationSchema().load(valid_name)


def test_valid_both_id_name():
    valid_id_name = {"id": "test", "name": "Funder One"}
    assert valid_id_name == FunderRelationSchema().load(valid_id_name)


def test_invalid_empty_relation():
    invalid_empty = {}
    with pytest.raises(ValidationError):
        data = FunderRelationSchema().load(invalid_empty)
