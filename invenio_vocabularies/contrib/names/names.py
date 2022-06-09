# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary names."""

from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2
from invenio_records.dumpers import ElasticsearchDumper
from invenio_records.dumpers.indexedat import IndexedAtDumperExt
from invenio_records.dumpers.relations import RelationDumperExt
from invenio_records.systemfields import RelationsField
from invenio_records_resources.factories.factory import RecordTypeFactory
from invenio_records_resources.records.systemfields import PIDListRelation

from ...records.pidprovider import PIDProviderFactory
from ...records.systemfields import BaseVocabularyPIDFieldContext
from ...services.permissions import PermissionPolicy
from ..affiliations.api import Affiliation
from .config import NamesSearchOptions, service_components
from .schema import NameSchema

name_relations = RelationsField(
    affiliations=PIDListRelation(
        "affiliations",
        keys=["name"],
        pid_field=Affiliation.pid,
        cache_key="affiliations",
    )
)

record_type = RecordTypeFactory(
    "Name",
    # Data layer
    pid_field_kwargs={
        "create": False,
        "provider": PIDProviderFactory.create(
            pid_type="names", base_cls=RecordIdProviderV2
        ),
        "context_cls": BaseVocabularyPIDFieldContext,
    },
    schema_version="1.0.0",
    schema_path="local://names/name-v1.0.0.json",
    record_relations=name_relations,
    record_dumper=ElasticsearchDumper(
        extensions=[
            RelationDumperExt("relations"),
            IndexedAtDumperExt(),
        ]
    ),
    # Service layer
    service_id="names",
    service_schema=NameSchema,
    search_options=NamesSearchOptions,
    service_components=service_components,
    permission_policy_cls=PermissionPolicy,
    # Resource layer
    endpoint_route="/names",
)
