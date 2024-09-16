# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary affiliations."""

from flask_resources import JSONSerializer, ResponseHandler
from invenio_db import db
from invenio_records.dumpers import SearchDumper
from invenio_records.dumpers.indexedat import IndexedAtDumperExt
from invenio_records_resources.factories.factory import RecordTypeFactory
from invenio_records_resources.records.systemfields import ModelPIDField
from invenio_records_resources.resources.records.headers import etag_headers

from invenio_vocabularies.services.permissions import PermissionPolicy

from .config import AffiliationsSearchOptions, service_components
from .schema import AffiliationSchema

record_type = RecordTypeFactory(
    "Affiliation",
    # Data layer
    pid_field_cls=ModelPIDField,
    pid_field_kwargs={
        "model_field_name": "pid",
    },
    model_cls_attrs={
        # cannot set to nullable=False because it would fail at
        # service level when create({}), see records-resources.
        "pid": db.Column(db.String(255), unique=True),
    },
    schema_version="1.0.0",
    schema_path="local://affiliations/affiliation-v1.0.0.json",
    index_name="affiliations-affiliation-v2.0.0",
    record_dumper=SearchDumper(
        model_fields={"pid": ("id", str)},
        extensions=[
            IndexedAtDumperExt(),
        ],
    ),
    # Service layer
    service_id="affiliations",
    service_schema=AffiliationSchema,
    search_options=AffiliationsSearchOptions,
    service_components=service_components,
    permission_policy_cls=PermissionPolicy,
    # Resource layer
    endpoint_route="/affiliations",
    resource_cls_attrs={
        "response_handlers": {
            "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                JSONSerializer(), headers=etag_headers
            ),
        }
    },
)
