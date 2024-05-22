# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Vocabularies is free software; you can redistringibute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Resources config."""

import marshmallow as ma
from flask_resources import (
    HTTPJSONException,
    ResourceConfig,
    create_error_handler,
    JSONSerializer,
    BaseListSchema,
    MarshmallowSerializer,
    ResponseHandler,
)
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.records.args import SearchRequestArgsSchema
from invenio_records_resources.services.base.config import ConfiguratorMixin
from invenio_records_resources.resources import (
    RecordResource,
    RecordResourceConfig,
    SearchRequestArgsSchema,
)
from .serializer import VocabularyL10NItemSchema


class TasksResourceConfig(ResourceConfig, ConfiguratorMixin):
    """Celery tasks resource config."""

    # Blueprint configuration
    blueprint_name = "tasks"
    url_prefix = "/tasks"
    routes = {"list": ""}


class VocabularySearchRequestArgsSchema(SearchRequestArgsSchema):
    """Vocabularies search request parameters."""

    tags = ma.fields.Str()
    active = ma.fields.Boolean()
    status = ma.fields.Boolean()


class VocabulariesResourceConfig(RecordResourceConfig):
    """Vocabulary resource configuration."""

    blueprint_name = "vocabularies"
    url_prefix = "/vocabularies"
    routes = {
        "list": "/<type>",
        "item": "/<type>/<pid_value>",
        "tasks": "/tasks",
    }

    request_view_args = {
        "pid_value": ma.fields.Str(),
        "type": ma.fields.Str(required=True),
    }

    request_search_args = VocabularySearchRequestArgsSchema

    response_handlers = {
        "application/json": ResponseHandler(JSONSerializer(), headers=etag_headers),
        "application/vnd.inveniordm.v1+json": ResponseHandler(
            MarshmallowSerializer(
                format_serializer_cls=JSONSerializer,
                object_schema_cls=VocabularyL10NItemSchema,
                list_schema_cls=BaseListSchema,
            ),
            headers=etag_headers,
        ),
    }


class VocabularyTypeResourceConfig(ResourceConfig, ConfiguratorMixin):
    """Vocabulary list resource config."""

    # /vocabulary/vocabulary_id
    # Blueprint configuration
    blueprint_name = "vocabulary_list"
    url_prefix = "/vocabularies"

    routes = {
        "all": "/",
        "list": "/vocabularies/<vocabulary_id>",
        "item": "/vocabularies/<vocabulary_id>/<vocabulary_type_id>",
    }

    # Request parsing
    request_read_args = {}
    request_view_args = {
        "vocabulary_id": ma.fields.String,
        "vocabulary_type_id": ma.fields.String,
    }
    request_search_args = VocabularySearchRequestArgsSchema

    error_handlers = {
        **ErrorHandlersMixin.error_handlers,
        # TODO: Add custom error handlers here
    }
