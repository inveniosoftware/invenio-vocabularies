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
from invenio_records.systemfields import ConstantField, ModelField
from invenio_records_resources.records.api import Record as RecordBase
from invenio_records_resources.records.systemfields import IndexField, \
    PIDField, PIDStatusCheckField

from . import models


class Vocabulary(RecordBase):
    """Example record API."""

    # Configuration
    model_cls = models.VocabularyMetadata

    # System fields
    schema = ConstantField(
        "$schema",
        "http://localhost/schemas/vocabularies/vocabulary-v1.0.0.json",
    )

    index = IndexField(
        "vocabularies-vocabulary-v1.0.0", search_alias="vocabularies"
    )

    pid = PIDField("id", provider=RecordIdProviderV2)
    vocabulary_type = ModelField()

    conceptpid = PIDField("conceptid", provider=RecordIdProviderV2)

    is_published = PIDStatusCheckField(status=PIDStatus.REGISTERED)
