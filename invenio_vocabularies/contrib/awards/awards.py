# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary awards."""
from flask_resources import (
    BaseListSchema,
    JSONSerializer,
    MarshmallowSerializer,
    ResponseHandler,
)
from invenio_db import db
from invenio_records.dumpers import ElasticsearchDumper
from invenio_records.dumpers.indexedat import IndexedAtDumperExt
from invenio_records.dumpers.relations import RelationDumperExt
from invenio_records.systemfields import RelationsField
from invenio_records_resources.factories.factory import RecordTypeFactory
from invenio_records_resources.records.systemfields import ModelPIDField, PIDRelation
from invenio_records_resources.resources.records.headers import etag_headers

from ...services.permissions import PermissionPolicy
from ..funders.api import Funder
from .config import AwardsSearchOptions, service_components
from .schema import AwardSchema
from .serializer import AwardL10NItemSchema

award_relations = RelationsField(
    funders=PIDRelation(
        "funder",
        keys=["name"],
        pid_field=Funder.pid,
        cache_key="funder",
    )
)

record_type = RecordTypeFactory(
    "Award",
    # Data layer
    pid_field_cls=ModelPIDField,
    pid_field_kwargs={
        "model_field_name": "pid",
    },
    model_cls_attrs={
        # cannot set to nullable=False because it would fail at
        # service level when create({}), see records-resources.
        "pid": db.Column(db.String, unique=True),
    },
    record_dumper=ElasticsearchDumper(
        model_fields={"pid": ("id", str)},
        extensions=[
            RelationDumperExt("relations"),
            IndexedAtDumperExt(),
        ],
    ),
    schema_version="1.0.0",
    schema_path="local://awards/award-v1.0.0.json",
    record_relations=award_relations,
    # Service layer
    service_id="awards",
    service_schema=AwardSchema,
    search_options=AwardsSearchOptions,
    service_components=service_components,
    permission_policy_cls=PermissionPolicy,
    # Resource layer
    endpoint_route="/awards",
    resource_cls_attrs={
        "response_handlers": {
            "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                MarshmallowSerializer(
                    format_serializer_cls=JSONSerializer,
                    object_schema_cls=AwardL10NItemSchema,
                    list_schema_cls=BaseListSchema,
                ),
                headers=etag_headers,
            ),
        }
    },
)
