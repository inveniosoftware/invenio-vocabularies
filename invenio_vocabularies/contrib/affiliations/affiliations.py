# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary affiliations."""

from invenio_records.dumpers import ElasticsearchDumper
from invenio_records.dumpers.indexedat import IndexedAtDumperExt
from invenio_records_resources.factories.factory import RecordTypeFactory

from ...records.pidprovider import PIDProviderFactory
from ...records.systemfields import BaseVocabularyPIDFieldContext
from ...services.permissions import PermissionPolicy
from .config import AffiliationsSearchOptions, service_components
from .schema import AffiliationSchema

record_type = RecordTypeFactory(
    "Affiliation",
    # Data layer
    pid_field_kwargs={
        "create": False,
        "provider": PIDProviderFactory.create(pid_type="aff"),
        "context_cls": BaseVocabularyPIDFieldContext,
    },
    schema_version="1.0.0",
    schema_path="local://affiliations/affiliation-v1.0.0.json",
    record_dumper=ElasticsearchDumper(
        extensions=[
            IndexedAtDumperExt(),
        ]
    ),
    # Service layer
    service_id="affiliations",
    service_schema=AffiliationSchema,
    search_options=AffiliationsSearchOptions,
    service_components=service_components,
    permission_policy_cls=PermissionPolicy,
    # Resource layer
    endpoint_route="/affiliations",
)
