# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary data API."""

from invenio_records.systemfields import ConstantField, RelatedModelField
from invenio_records_resources.records.api import Record
from invenio_records_resources.records.systemfields import IndexField, PIDField

from .models import VocabularyMetadata, VocabularyType
from .pidprovider import VocabularyIdProvider
from .systemfields import VocabularyPIDFieldContext


class Vocabulary(Record):
    """A generic vocabulary record."""

    # Configuration
    model_cls = VocabularyMetadata

    # System fields
    # TODO: Can schema name be changed (remove localhost)
    schema = ConstantField(
        "$schema",
        "local://vocabularies/vocabulary-v1.0.0.json",
    )

    index = IndexField(
        "vocabularies-vocabulary-v1.0.0", search_alias="vocabularies"
    )

    #: Disable the metadata system field.
    metadata = None

    type = RelatedModelField(VocabularyType, required=True)

    pid = PIDField(
        'id',
        provider=VocabularyIdProvider,
        context_cls=VocabularyPIDFieldContext,
        create=False,
    )
