# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Vocabulariess is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test award schema."""

import pytest
from marshmallow import ValidationError

from invenio_vocabularies.contrib.awards.schema import (
    AwardRelationSchema,
    AwardSchema,
    FundingRelationSchema,
)


#
# AwardRelationSchema
#
def test_valid_full(app, award_full_data):
    loaded = AwardSchema().load(award_full_data)
    award_full_data["pid"] = award_full_data.pop("id")
    assert award_full_data == loaded


def test_valid_minimal():
    valid_minimal = {"id": "755021", "number": "755021"}
    assert {
        "pid": "755021",
        "number": "755021",
    } == AwardSchema().load(valid_minimal)


def test_invalid_no_number(app):
    invalid_no_number = {
        "identifiers": [{"identifier": "10.5281/zenodo.9999999", "scheme": "doi"}]
    }
    with pytest.raises(ValidationError):
        data = AwardSchema().load(invalid_no_number)


def test_invalid_empty_number(app):
    invalid_empty_number = {"id": "755021", "number": ""}

    with pytest.raises(ValidationError):
        data = AwardSchema().load(invalid_empty_number)


def test_invalid_empty_pid(app):
    invalid_empty_pid = {"id": "", "number": "755021"}

    with pytest.raises(ValidationError):
        AwardSchema().load(invalid_empty_pid)


def test_award_funder_name(app):
    with_funder_name = {
        "id": "755021",
        "number": "755021",
        "funder": {
            "name": "custom funder",
        },
    }
    assert {
        "pid": "755021",
        "number": "755021",
        "funder": {
            "name": "custom funder",
        },
    } == AwardSchema().load(with_funder_name)


def test_award_funder_id(app):
    with_funder_id = {
        "id": "755021",
        "number": "755021",
        "funder": {
            "id": "01ggx4157",
        },
    }
    assert {
        "pid": "755021",
        "number": "755021",
        "funder": {
            "id": "01ggx4157",
        },
    } == AwardSchema().load(with_funder_id)


#
# AwardRelationSchema
#


def test_valid_id():
    valid_id = {
        "id": "test",
    }
    assert valid_id == AwardRelationSchema().load(valid_id)


def test_valid_number_title():
    valid_data = {"number": "123456", "title": {"en": "Test title."}}
    assert valid_data == AwardRelationSchema().load(valid_data)


def test_invalid_empty():
    invalid_data = {}
    with pytest.raises(ValidationError):
        data = AwardRelationSchema().load(invalid_data)


def test_invalid_number_type():
    invalid_data = {"number": 123}
    with pytest.raises(ValidationError):
        data = AwardRelationSchema().load(invalid_data)


#
# FundingRelationSchema
#


AWARD = {"title": {"en": "Some award"}, "number": "755021"}

FUNDER = {
    "name": "Someone",
}


def test_valid_award_funding():
    valid_funding = {"award": AWARD}
    assert valid_funding == FundingRelationSchema().load(valid_funding)

    # Test a valid award with different representation
    valid_funding = {"award": {"id": "test-award-id"}}
    assert valid_funding == FundingRelationSchema().load(valid_funding)


def test_invalid_award_funding():
    invalid_funding = {"award": {"identifiers": [AWARD.get("identifiers")]}}
    with pytest.raises(ValidationError):
        data = FundingRelationSchema().load(invalid_funding)


def test_valid_funder_funding():
    valid_funding = {"funder": FUNDER}
    assert valid_funding == FundingRelationSchema().load(valid_funding)

    # Test a valid funder with different representation
    valid_funding = {"funder": {"id": "test-funder-id"}}
    assert valid_funding == FundingRelationSchema().load(valid_funding)


def test_invalid_funder_funding():
    invalid_funding = {"funder": {"identifiers": [AWARD.get("identifiers")]}}
    with pytest.raises(ValidationError):
        data = FundingRelationSchema().load(invalid_funding)


def test_valid_award_funder_funding():
    valid_funding = {"funder": FUNDER, "award": AWARD}
    assert valid_funding == FundingRelationSchema().load(valid_funding)


def test_invalid_empty_funding():
    invalid_funding = {}
    with pytest.raises(ValidationError):
        data = FundingRelationSchema().load(invalid_funding)
