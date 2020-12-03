# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary API."""
from invenio_pidstore.models import PIDStatus
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records.dumpers import ElasticsearchDumper
from invenio_records.systemfields import ConstantField, ModelField
from invenio_records_resources.records.api import Record as RecordBase
from invenio_records_resources.records.systemfields import IndexField, \
    PIDField, PIDStatusCheckField

from . import models
from .dumper_extensions import VocabularyTypeElasticsearchDumperExt


class Vocabulary(RecordBase):
    """Example record API."""

    # Configuration
    model_cls = models.VocabularyMetadata

    dumper = ElasticsearchDumper(extensions=[VocabularyTypeElasticsearchDumperExt()])

    # System fields
    schema = ConstantField(
        "$schema",
        "http://127.0.0.1:5000/schemas/vocabularies/vocabulary-v1.0.0.json"
    )

    index = IndexField(
        "vocabularies-vocabulary-v1.0.0", search_alias="vocabularies"
    )

    pid = PIDField("id", provider=RecordIdProviderV2)
    vocabulary_type_id = ModelField()

