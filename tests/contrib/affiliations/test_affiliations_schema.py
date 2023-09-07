# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Affiliations Marshmallow schema tests."""

import pytest
from marshmallow import ValidationError

from invenio_vocabularies.contrib.affiliations.schema import (
    AffiliationRelationSchema,
    AffiliationSchema,
)


def test_valid_full(app, affiliation_full_data):
    loaded = AffiliationSchema().load(affiliation_full_data)
    affiliation_full_data["pid"] = affiliation_full_data.pop("id")
    assert affiliation_full_data == loaded


def test_valid_minimal(app):
    data = {
        "id": "test",
        "name": "Test affiliation",
    }
    loaded = AffiliationSchema().load(data)
    assert {
        "pid": "test",
        "name": "Test affiliation",
    } == loaded


def test_invalid_no_name(app):
    invalid = {
        "acronym": "TEST",
        "id": "aff-1",
        "identifiers": [{"identifier": "03yrm5c26", "scheme": "ror"}],
        "title": {"en": "Test affiliation", "es": "Afiliacion de test"},
    }
    with pytest.raises(ValidationError):
        data = AffiliationSchema().load(invalid)


#
# AffiliationRelationSchema
#
def test_valid_id():
    valid_id = {
        "id": "test",
    }
    assert valid_id == AffiliationRelationSchema().load(valid_id)


def test_valid_name():
    valid_name = {"name": "Entity One"}
    assert valid_name == AffiliationRelationSchema().load(valid_name)


def test_valid_both_id_name():
    valid_id_name = {"id": "test", "name": "Entity One"}
    assert valid_id_name == AffiliationRelationSchema().load(valid_id_name)


def test_invalid_empty():
    invalid_empty = {}
    with pytest.raises(ValidationError):
        data = AffiliationRelationSchema().load(invalid_empty)
