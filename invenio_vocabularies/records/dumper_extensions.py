# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary dumper extension."""

from invenio_records.dumpers import ElasticsearchDumperExt

from invenio_vocabularies.records.models import VocabularyType


class VocabularyTypeElasticsearchDumperExt(ElasticsearchDumperExt):
    """vocabulary dumper."""

    def dump(self, record, data):
        """Dump data."""
        vocabulary_type_id = data.get("vocabulary_type_id")
        if vocabulary_type_id:
            data["vocabulary_type"] = VocabularyType.query.get(
                vocabulary_type_id
            ).name
            data["vocabulary_type_id"] = VocabularyType.query.get(
                vocabulary_type_id
            ).id
        super().dump(record, data)

    def load(self, data, record_cls):
        """Load data."""
        vocabulary_type_id = data.get("vocabulary_type_id")
        if vocabulary_type_id:
            data["vocabulary_type"] = VocabularyType.query.get(
                vocabulary_type_id
            ).name
            data["vocabulary_type_id"] = VocabularyType.query.get(
                vocabulary_type_id
            ).id
        super().load(data, record_cls)
