# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Fixtures tests."""

from pathlib import Path

import pytest

from invenio_vocabularies.fixtures import VocabularyFixture


def test_base_fixture(app):
    """Simulates looping through two vocabularies.

    Reports a set of errors per vocabulary. In this case each vocab has one.
    The first fails on a transformer and the second fails on a writer.
    Note that the entries are not the first one, so only the ones with errors
    are returned.
    """
    filepath = Path(__file__).parent / "vocabularies.yaml"
    fixture = VocabularyFixture(filepath=filepath)
    results = fixture.load()

    invalid_tr = next(results)
    assert len(invalid_tr) == 1
    result = invalid_tr[0]
    assert result.entry == -1
    assert ["TestTransformer: Value cannot be negative"] == result.errors

    invalid_wr = next(results)
    assert len(invalid_wr) == 1
    result = invalid_wr[0]
    assert result.entry == 2
    assert ["FailingTestWriter: 2 value found."] == result.errors

    with pytest.raises(StopIteration):
        next(results)  # stops after the two configured vocabularies
