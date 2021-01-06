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
            data["vocabulary_type"] = VocabularyType.query.get(
                vocabulary_type_id
            ).name

    def load(self, data, record_cls):
        """Load the data into a record."""
        # TODO: The below line is a temporary **HACK** and is **WRONG**
        # The entire dumper should be removed!
        # The vocabulary_type requires some caching similar to pid ModelField
        # and the dumper is not the right place to do that!
        # data.pop("vocabulary_type", None)
