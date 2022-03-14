# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary funders."""

from invenio_db import db
from invenio_pidstore.models import PIDStatus
from invenio_records.dumpers import ElasticsearchDumper
from invenio_records.systemfields import ModelField
from invenio_records_resources.factories.factory import RecordTypeFactory
from invenio_records_resources.records.systemfields import ModelPIDField
from sqlalchemy_utils.types import ChoiceType

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
        "pid_status": db.Column(
            ChoiceType(PIDStatus, impl=db.CHAR(1))
        )
    },
    record_cls_attrs={
        "pid_status": ModelField(dump_type=str)
    },
    record_dumper=ElasticsearchDumper(
        model_fields={'pid': ('pid', str)}
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
