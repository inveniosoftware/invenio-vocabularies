# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test models."""

import pytest

from invenio_vocabularies.records.models import VocabularyScheme


#
# Tests
#
def test_well_formed_subtype(database):
    with pytest.raises(AssertionError):
        VocabularyScheme.create(
            id="foo,bar,baz", parent_id="subjects", name="Foo Bar Baz", uri=""
        )

    with pytest.raises(AssertionError):
        VocabularyScheme.create(
            id="foo:bar", parent_id="subjects", name="Foo: Bar", uri=""
        )

    assert VocabularyScheme.create(id="foo", parent_id="subjects", name="Foo", uri="")
