# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Module API tests."""

# import pytest

# from invenio_vocabularies.api import VocabularyBackend
# from invenio_vocabularies.records.api import Vocabulary


# def test_backend_get(app, db, client, example_record, service):
#     """Test get method of vocabulary backend."""
#     assert example_record._record == VocabularyBackend().get(
# example_record.id)


# @pytest.mark.skip
# def test_backend_get_all(app, db, client, example_record, identity_simple,
#                          service, example_data):

#     record1_languages = service.create(
#         identity=identity_simple,
#         data=dict(**example_data, vocabulary_type_id=1),
#     )
#     record2_languages = service.create(
#         identity=identity_simple,
#         data=dict(**example_data, vocabulary_type_id=1),
#     )
#     record1_licenses = service.create(
#         identity=identity_simple,
#         data=dict(**example_data, vocabulary_type_id=2),
#     )
#     Vocabulary.index.refresh()
#     all_list = VocabularyBackend().get_all('languages')
#     assert len(all_list["hits"]["hits"]) == 3


# @pytest.mark.skip
# def test_backend_locale(app, example_record, monkeypatch):
#     """Test the correctness of localization."""
#     record = VocabularyBackend().get(example_record.id)  # wrapper
#     monkeypatch.setattr("babel.default_locale", lambda: "en")

#     assert record.get_title("en") == "Test title"
#     assert record.get_title("sv") == "Test title"  # uses default
#     assert record.get_title("fr") == "Titre test"
