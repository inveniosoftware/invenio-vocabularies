# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary funders."""

from invenio_db import db
from invenio_records.dumpers import ElasticsearchDumper
from invenio_records.dumpers.indexedat import IndexedAtDumperExt
from invenio_records_resources.factories.factory import RecordTypeFactory
from invenio_records_resources.records.systemfields import ModelPIDField

from ...services.permissions import PermissionPolicy
from .config import FundersSearchOptions, service_components
from .schema import FunderSchema

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
        "pid": db.Column(db.String, unique=True),
    },
    record_dumper=ElasticsearchDumper(
        model_fields={'pid': ('id', str)},
        extensions=[
            IndexedAtDumperExt(),
        ]
    ),
    schema_version="1.0.0",
    schema_path="local://funders/funder-v1.0.0.json",
    # Service layer
    service_schema=FunderSchema,
    search_options=FundersSearchOptions,
    service_components=service_components,
    permission_policy_cls=PermissionPolicy,
    # Resource layer
    endpoint_route='/funders',
)
