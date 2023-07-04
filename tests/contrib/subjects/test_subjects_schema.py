# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Subjects schema tests."""

from copy import copy

import pytest
from marshmallow import ValidationError

from invenio_vocabularies.contrib.subjects.schema import (
    SubjectRelationSchema,
    SubjectSchema,
)


class TestSubjectSchema:
    def test_valid_full(self, subject_full_data):
        loaded = SubjectSchema().load(subject_full_data)
        assert subject_full_data == loaded

    def test_invalid_missing_field(self, subject_full_data):
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

        # no subject
        invalid = copy(subject_full_data)
        del invalid["subject"]
        with pytest.raises(ValidationError):
            SubjectSchema().load(invalid)


class TestSubjectRelationSchema:
    def test_valid_id(self):
        valid_id = {
            "id": "test",
        }
        assert valid_id == SubjectRelationSchema().load(valid_id)

    def test_valid_subject(self):
        valid_subject = {"subject": "Entity One"}
        assert valid_subject == SubjectRelationSchema().load(valid_subject)

    def test_invalid_empty(self):
        invalid_empty = {}
        with pytest.raises(ValidationError):
            SubjectRelationSchema().load(invalid_empty)

    def test_dump(self):
        subject = {"subject": "Entity One"}
        assert {"subject": "Entity One"} == SubjectRelationSchema().dump(subject)

        subject = {"subject": "Entity One", "scheme": "scheme A"}
        assert subject == SubjectRelationSchema().dump(subject)
