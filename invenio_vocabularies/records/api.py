# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary API."""

from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records.dumpers import ElasticsearchDumper
from invenio_records.systemfields import ConstantField, ModelField
from invenio_records_resources.records.api import Record as RecordBase
from invenio_records_resources.records.systemfields import IndexField, PIDField

from .dumper_extensions import VocabularyTypeElasticsearchDumperExt
from .models import VocabularyMetadata
from .systemfields.VocabularyTypeField import VocabularyTypeField


class Vocabulary(RecordBase):
    """Example record API."""

    # Configuration
    model_cls = VocabularyMetadata

    dumper = ElasticsearchDumper(
        extensions=[VocabularyTypeElasticsearchDumperExt()]
    )

    # System fields
    schema = ConstantField(
        "$schema",
        "https://localhost/schemas/vocabularies/vocabulary-v1.0.0.json",
    )

    index = IndexField(
        "vocabularies-vocabulary-v1.0.0", search_alias="vocabularies"
    )

    # TODO: This should be changed to use something else than the recidv2
    pid = PIDField("id", provider=RecordIdProviderV2)

    vocabulary_type_id = ModelField()

    vocabulary_type = VocabularyTypeField(dump=False)
