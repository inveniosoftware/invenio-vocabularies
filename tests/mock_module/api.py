# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


"""Example of a record API."""

from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records.dumpers import ElasticsearchDumper
from invenio_records.dumpers.relations import RelationDumperExt
from invenio_records.systemfields import ConstantField, RelationsField
from invenio_records_resources.records.api import Record as RecordBase
from invenio_records_resources.records.systemfields import IndexField, \
    PIDField, PIDListRelation

from invenio_vocabularies.records.api import Vocabulary

from . import models


class Record(RecordBase):
    """Example bibliographic record API."""

    model_cls = models.RecordMetadata
    schema = ConstantField(
        '$schema', 'local://records/record-v1.0.0.json')
    index = IndexField('records-record-v1.0.0', search_alias='records')
    pid = PIDField('id', provider=RecordIdProviderV2)

    # Definitions of relationships from a bibliographic record to the
    # generic vocabularies.
    relations = RelationsField(
        languages=PIDListRelation(
            'metadata.languages',
            attrs=['id', 'title'],
            pid_field=Vocabulary.pid.with_type_ctx('languages')
        ),
    )

    dumper = ElasticsearchDumper(
        extensions=[
            RelationDumperExt('relations'),
        ]
    )
