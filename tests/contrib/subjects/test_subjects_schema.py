# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-FileCopyrightText: 2021 Northwestern University.
# SPDX-FileCopyrightText: 2024 University of Münster.
# SPDX-License-Identifier: MIT

"""Subjects schema tests."""

from copy import copy

import pytest
from marshmallow import ValidationError

from invenio_vocabularies.contrib.subjects.schema import SubjectSchema


def test_valid_full(app, subject_full_data, expected_subject_full_data):
    loaded = SubjectSchema().load(subject_full_data)
    assert expected_subject_full_data == loaded


def test_invalid_missing_field(app, subject_full_data):
    # no id
    invalid = copy(subject_full_data)
    del invalid["id"]
    with pytest.raises(ValidationError):
        SubjectSchema().load(invalid)

    # no scheme
    invalid = copy(subject_full_data)
    del invalid["scheme"]
    with pytest.raises(ValidationError):
        SubjectSchema().load(invalid)
