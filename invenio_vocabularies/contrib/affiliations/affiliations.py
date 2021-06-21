# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary affiliations."""

from invenio_records_resources.factories.factory import RecordTypeFactory

from ...records.pidprovider import PIDProviderFactory, VocabularyIdProvider
from ...records.systemfields import BaseVocabularyPIDFieldContext
from ...services.permissions import PermissionPolicy
from .config import AffiliationsSearchOptions, service_components
from .schema import AffiliationSchema

affiliation_record_type = RecordTypeFactory(
    "Affiliation",
    # Data layer
    pid_provider_cls=PIDProviderFactory.create(pid_type='aff'),
    pid_ctx_cls=BaseVocabularyPIDFieldContext,
    pid_create=False,
    schema_version="1.0.0",
    schema_path="local://affiliations/affiliation-v1.0.0.json",
    # Service layer
    endpoint_route='/affiliations',
    record_type_service_schema=AffiliationSchema,
    search_options=None,
    service_components=service_components,
    permission_policy_cls=PermissionPolicy,
)
