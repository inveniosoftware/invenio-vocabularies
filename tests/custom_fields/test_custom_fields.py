# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022-2024 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test custom fields."""

import pytest
from invenio_records_resources.records.systemfields import PIDListRelation, PIDRelation
from marshmallow import Schema, ValidationError

from invenio_vocabularies.services.custom_fields import VocabularyCF


@pytest.fixture(scope="module")
def vocabulary_cf():
    return VocabularyCF("test", "test")


@pytest.fixture(scope="module")
def TestSchema(vocabulary_cf):
    return Schema.from_dict({"test": vocabulary_cf.field})


@pytest.fixture(scope="module")
def TestUISchema(vocabulary_cf):
    return Schema.from_dict({"test": vocabulary_cf.ui_field})


def test_relation_cls(vocabulary_cf):
    assert vocabulary_cf.relation_cls == PIDRelation

    multi = VocabularyCF("test", "test", multiple=True)
    assert multi.relation_cls == PIDListRelation


def test_cf_mapping(vocabulary_cf):
    # this will be useful when implementing compatibility with OS
    assert vocabulary_cf.mapping == {
        "type": "object",
        "properties": {
            "@v": {"type": "keyword"},
            "id": {"type": "keyword"},
            "title": {"type": "object", "dynamic": "true"},
        },
    }


def test_field_load(TestSchema):
    vocab = {"test": {"id": "test", "title": {"en": "Test"}}}
    assert TestSchema().load(vocab) == {"test": {"id": "test"}}


def test_field_dump(TestSchema):
    vocab = {"test": {"id": "test", "title": {"en": "Test"}}}
    assert TestSchema().load(vocab) == {"test": {"id": "test"}}


def test_ui_field_dump(app, TestUISchema):
    # app is needed for babel local setup
    # no load test since it's never used for loading
    vocab = {
        "test": {
            "id": "test",
            "title": {"en": "Test"},
            "description": {"en": "Test description"},
            "props": {"key": "value"},
            "icon": "icon.png",
            "tags": ["tag1", "tag2"],
        }
    }

    expected_vocab = {
        "test": {
            "id": "test",
            "title_l10n": "Test",
            "description_l10n": "Test description",
            "props": {"key": "value"},
            "icon": "icon.png",
            "tags": ["tag1", "tag2"],
        }
    }
    assert TestUISchema().dump(vocab) == expected_vocab


def test_options(lang_data_many, identity):
    cf = VocabularyCF("test", "languages")
    expected_options = [
        {
            "id": lang,
            "title_l10n": "English",
            "icon": "file-o",
            "props": {
                "akey": "avalue",
            },
        }
        for lang in ["fr", "tr", "gr", "ger", "es"]
    ]

    assert cf.options(identity) == expected_options


def test_vocab_field_required():
    cf = VocabularyCF("test", "test", field_args={"required": True})
    schema = Schema.from_dict({"test": cf.field})()

    with pytest.raises(ValidationError):
        schema.load({})


def test_vocab_ui_field_required():
    cf = VocabularyCF("test", "test", field_args={"required": True})
    schema = Schema.from_dict({"test": cf.ui_field})()

    with pytest.raises(ValidationError):
        schema.load({})
