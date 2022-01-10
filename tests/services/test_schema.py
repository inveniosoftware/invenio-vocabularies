# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Service schemas tests."""

import pytest
from marshmallow import ValidationError

from invenio_vocabularies.services.schema import TaskSchema


def test_valid_minimal():
    valid_minimal = {
        "reader": {
            "type": "test"
        },
        "writers": [{"type": "test"}]
    }
    assert valid_minimal == TaskSchema().load(valid_minimal)


def test_valid_full():
    valid_full = {
        "reader": {
            "type": "test",
            "args": {
                "one": 1,
                "two": "two"
            }
        },
        "transformers": [{
            "type": "test",
            "args": {
                "one": 1,
                "two": "two"
            }
        }, {
            "type": "testtoo",
            "args": {
                "one": "1",
                "two": 2
            }
        }],
        "writers": [{
            "type": "test",
            "args": {
                "one": 1,
                "two": "two"
            }
        }, {
            "type": "testtoo",
            "args": {
                "one": "1",
                "two": 2
            }
        }],
    }
    assert valid_full == TaskSchema().load(valid_full)


@pytest.mark.parametrize("invalid", [
    {},
    {
        "reader": [{"type": "test"}, {"type": "testtoo"}],
        "writers": [{"type": "test"}]
    },
    {
        "reader": {"type": "testtoo"},
        "writers": {"type": "test"}
    },
    {
        "reader": {"type": "testtoo"},
        "transformers": {"type": "test"},
        "writers": [{"type": "test"}]
    },
    {
        "reader": {"type": "testtoo"},
    },
    {
        "writers": [{"type": "test"}]
    },
])
def test_invalid_empty(invalid):
    with pytest.raises(ValidationError):
        data = TaskSchema().load(invalid)
