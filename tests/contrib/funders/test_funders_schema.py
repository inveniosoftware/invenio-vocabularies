# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test funder schema."""

import pytest
from marshmallow import ValidationError

from invenio_vocabularies.contrib.funders.schema import FunderRelationSchema


def test_valid_full():
    valid_full = {
        "name": "Someone",
        "identifier": "10.5281/zenodo.9999999",
        "scheme": "doi"
    }
    assert valid_full == FunderRelationSchema().load(valid_full)


def test_valid_minimal():
    valid_minimal = {
        "name": "Someone"
    }
    assert valid_minimal == FunderRelationSchema().load(valid_minimal)


def test_invalid_no_name():
    invalid_no_name = {
        "identifier": "10.5281/zenodo.9999999",
        "scheme": "doi"
    }
    with pytest.raises(ValidationError):
        data = FunderRelationSchema().load(invalid_no_name)
