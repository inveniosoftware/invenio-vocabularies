# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary affiliations."""

from invenio_records_resources.factories.factory import RecordTypeFactory

from ...records.pidprovider import VocabularyIdProvider
from ...services.permissions import PermissionPolicy
from .pidprovider import AffiliationProvider
from .schema import AffiliationSchema

affiliation_record_type = RecordTypeFactory(
    "Affiliation",
    AffiliationSchema,
    permission_policy_cls=PermissionPolicy,
    pid_provider_cls=AffiliationProvider,
    schema_version="1.0.0",
    schema_path="local://affiliations/affiliation-v1.0.0.json",
    endpoint_route='/affiliations'
)
