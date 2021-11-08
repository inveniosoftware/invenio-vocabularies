# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test award schema."""

import pytest
from marshmallow import ValidationError

from invenio_vocabularies.contrib.awards.schema import AwardRelationSchema, \
    FundingRelationSchema


#
# AwardRelationSchema
#
def test_valid_full():
    valid_full = {
        "title": "Some award",
        "number": "100",
        "identifier": "10.5281/zenodo.9999999",
        "scheme": "doi"
    }
    assert valid_full == AwardRelationSchema().load(valid_full)


def test_valid_minimal():
    valid_minimal = {
        "title": "Some award",
        "number": "100",
    }
    assert valid_minimal == AwardRelationSchema().load(valid_minimal)


def test_invalid_no_title():
    invalid_no_title = {
        "number": "100",
        "identifier": "10.5281/zenodo.9999999",
        "scheme": "doi"
    }
    with pytest.raises(ValidationError):
        data = AwardRelationSchema().load(invalid_no_title)


def test_invalid_no_number():
    invalid_no_number = {
        "title": "Some award",
        "identifier": "10.5281/zenodo.9999999",
        "scheme": "doi"
    }
    with pytest.raises(ValidationError):
        data = AwardRelationSchema().load(invalid_no_number)


#
# FundingRelationSchema
#

AWARD = {
    "title": "Some award",
    "number": "100",
    "identifier": "10.5281/zenodo.9999999",
    "scheme": "doi"
}

FUNDER = {
    "name": "Someone",
    "identifier": "10.5281/zenodo.9999999",
    "scheme": "doi"
}


def test_valid_award_funding():
    valid_funding = {
        "award": AWARD
    }
    assert valid_funding == FundingRelationSchema().load(valid_funding)


def test_valid_funder_funding():
    valid_funding = {
        "funder": FUNDER
    }
    assert valid_funding == FundingRelationSchema().load(valid_funding)


def test_valid_award_funder_funding():
    valid_funding = {
        "funder": FUNDER,
        "award": AWARD
    }
    assert valid_funding == FundingRelationSchema().load(valid_funding)


def test_invalid_empty_funding():
    invalid_funding = {}
    with pytest.raises(ValidationError):
        data = FundingRelationSchema().load(invalid_funding)
