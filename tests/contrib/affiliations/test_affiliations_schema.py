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

from invenio_vocabularies.contrib.affiliations.schema import AffiliationSchema


def test_valid_full(affiliation_full_data):
    loaded = AffiliationSchema().load(affiliation_full_data)
    assert affiliation_full_data == loaded


def test_valid_minimal():
    data = {
        "name": "Test affiliation",
    }
    loaded = AffiliationSchema().load(data)
    assert data == loaded


def test_invalid_no_name():
    invalid = {
        "acronym": "TEST",
        "id": "aff-1",
        "identifiers": [
            {"identifier": "03yrm5c26", "scheme": "ror"}
        ],
        "title": {
            "en": "Test affiliation",
            "es": "Afiliacion de test"
        }
    }
    with pytest.raises(ValidationError):
        data = AffiliationSchema().load(invalid)
