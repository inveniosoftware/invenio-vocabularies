# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary funders."""

from flask_resources import (
    BaseListSchema,
    JSONSerializer,
    MarshmallowSerializer,
    ResponseHandler,
)
from invenio_db import db
from invenio_records.dumpers import SearchDumper
from invenio_records.dumpers.indexedat import IndexedAtDumperExt
from invenio_records_resources.factories.factory import RecordTypeFactory
from invenio_records_resources.records.systemfields import ModelPIDField
from invenio_records_resources.resources.records.headers import etag_headers

from invenio_vocabularies.services.permissions import PermissionPolicy

from .config import FundersSearchOptions, service_components
from .schema import FunderSchema
from .serializer import FunderL10NItemSchema

record_type = RecordTypeFactory(
    "Funder",
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
    record_dumper=SearchDumper(
        model_fields={"pid": ("id", str)},
        extensions=[
            IndexedAtDumperExt(),
        ],
    ),
    schema_version="1.0.0",
    schema_path="local://funders/funder-v1.0.0.json",
    index_name="funders-funder-v2.0.0",
    # Service layer
    service_id="funders",
    service_schema=FunderSchema,
    search_options=FundersSearchOptions,
    service_components=service_components,
    permission_policy_cls=PermissionPolicy,
    # Resource layer
    endpoint_route="/funders",
    resource_cls_attrs={
        "response_handlers": {
            "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                MarshmallowSerializer(
                    format_serializer_cls=JSONSerializer,
                    object_schema_cls=FunderL10NItemSchema,
                    list_schema_cls=BaseListSchema,
                ),
                headers=etag_headers,
            ),
        }
    },
)
