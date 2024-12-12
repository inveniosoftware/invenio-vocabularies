# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary names."""

from flask_resources import JSONSerializer, ResponseHandler
from invenio_db import db
from invenio_records.dumpers import SearchDumper
from invenio_records.dumpers.indexedat import IndexedAtDumperExt
from invenio_records.dumpers.relations import RelationDumperExt
from invenio_records.systemfields import ModelField, RelationsField
from invenio_records_resources.factories.factory import RecordTypeFactory
from invenio_records_resources.records.systemfields import (
    ModelPIDField,
    PIDListRelation,
)
from invenio_records_resources.resources.records.headers import etag_headers

from invenio_vocabularies.contrib.names.permissions import NamesPermissionPolicy

from ..affiliations.api import Affiliation
from .config import NamesSearchOptions, service_components
from .schema import NameSchema

name_relations = RelationsField(
    affiliations=PIDListRelation(
        "affiliations",
        keys=["name", "acronym"],
        pid_field=Affiliation.pid,
        cache_key="affiliations",
    )
)

record_type = RecordTypeFactory(
    "Name",
    # Data layer
    pid_field_cls=ModelPIDField,
    pid_field_kwargs={
        "model_field_name": "pid",
    },
    model_cls_attrs={
        # cannot set to nullable=False because it would fail at
        # service level when create({}), see records-resources.
        "pid": db.Column(db.String(255), unique=True),
        "internal_id": db.Column(db.String(255), nullable=True, index=True),
    },
    schema_version="1.0.0",
    schema_path="local://names/name-v1.0.0.json",
    index_name="names-name-v2.0.0",
    record_cls_attrs={"internal_id": ModelField("internal_id", dump=False)},
    record_relations=name_relations,
    record_dumper=SearchDumper(
        model_fields={"pid": ("id", str)},
        extensions=[
            RelationDumperExt("relations"),
            IndexedAtDumperExt(),
        ],
    ),
    # Service layer
    service_id="names",
    service_schema=NameSchema,
    search_options=NamesSearchOptions,
    service_components=service_components,
    permission_policy_cls=NamesPermissionPolicy,
    # Resource layer
    endpoint_route="/names",
    resource_cls_attrs={
        "response_handlers": {
            "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
            "application/vnd.inveniordm.v1+json": ResponseHandler(
                JSONSerializer(), headers=etag_headers
            ),
        }
    },
)
