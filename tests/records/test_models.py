# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test models."""


import pytest

from invenio_vocabularies.records.models import VocabularySubtype, \
    VocabularyType


#
# Tests
#
def test_well_formed_subtype(database):
    VocabularyType.create(id='subjects', pid_type='sub')

    with pytest.raises(AssertionError):
        VocabularySubtype.create(
            id='foo,bar,baz', vocabulary_id='subjects',
            label="Foo Bar Baz", prefix_url=""
        )

    with pytest.raises(AssertionError):
        VocabularySubtype.create(
            id='foo:bar', vocabulary_id='subjects',
            label="Foo: Bar", prefix_url=""
        )

    assert VocabularySubtype.create(
        id='foo', vocabulary_id='subjects',
        label="Foo", prefix_url=""
    )
