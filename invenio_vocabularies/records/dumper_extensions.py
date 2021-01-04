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

from .models import VocabularyType


class VocabularyTypeElasticsearchDumperExt(ElasticsearchDumperExt):
    """Elasticsearch vocabulary dumper."""

    def dump(self, record, data):
        """Dump the data from a record."""
        vocabulary_type_id = data.get("vocabulary_type_id")
        if vocabulary_type_id:
            # FIXME: class method in the model class? (e.g. query_by_name)
            data["vocabulary_type"] = VocabularyType.query.get(
                vocabulary_type_id
            ).name

    def load(self, data, record_cls):
        """Load the data into a record."""
        data.pop("vocabulary_type", None)
