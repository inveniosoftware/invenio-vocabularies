# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary subjects."""

from flask_resources import JSONSerializer, ResponseHandler
from invenio_records.dumpers import SearchDumper
from invenio_records.dumpers.indexedat import IndexedAtDumperExt
from invenio_records_resources.factories.factory import RecordTypeFactory
from invenio_records_resources.resources.records.headers import etag_headers

from ...records.pidprovider import PIDProviderFactory
from ...records.systemfields import BaseVocabularyPIDFieldContext
from ...services.permissions import PermissionPolicy
from .config import SubjectsSearchOptions, service_components
from .schema import SubjectSchema

record_type = RecordTypeFactory(
    "Subject",
    # Data layer
    pid_field_kwargs={
        "create": False,
        "provider": PIDProviderFactory.create(pid_type="sub"),
        "context_cls": BaseVocabularyPIDFieldContext,
    },
    schema_version="1.0.0",
    schema_path="local://subjects/subject-v1.0.0.json",
    record_dumper=SearchDumper(
        extensions=[
            IndexedAtDumperExt(),
        ]
    ),
    # Service layer
    service_id="subjects",
    service_schema=SubjectSchema,
    search_options=SubjectsSearchOptions,
    service_components=service_components,
    permission_policy_cls=PermissionPolicy,
    # Resource layer
    endpoint_route="/subjects",
    resource_cls_attrs={
        "response_handlers": {
            "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                JSONSerializer(), headers=etag_headers
            ),
        }
    },
)
