# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2024 Uni Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary resource."""

import json

import marshmallow as ma
from flask import g
from flask_resources import (
    BaseListSchema,
    JSONSerializer,
    MarshmallowSerializer,
    ResponseHandler,
    resource_requestctx,
    response_handler,
)
from invenio_access.permissions import system_identity
from invenio_records_resources.resources import (
    RecordResource,
    RecordResourceConfig,
    SearchRequestArgsSchema,
)
from invenio_records_resources.resources.records.headers import etag_headers
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_headers,
    request_search_args,
    request_view_args,
    route,
)
from invenio_records_resources.resources.records.utils import search_preference
from marshmallow import fields

from invenio_vocabularies.proxies import current_service
from invenio_vocabularies.services.service import VocabularyTypeService

from .serializer import VocabularyL10NItemSchema


#
# Request args
#
class VocabularySearchRequestArgsSchema(SearchRequestArgsSchema):
    """Add parameter to parse tags."""

    tags = fields.Str()


#
# Resource config
#
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


#
# Resource
#
class VocabulariesResource(RecordResource):
    """Resource for generic vocabularies.

    Provide the API /api/vocabularies/
    """

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        rules = super().create_url_rules()
        rules.append(
            route("POST", routes["tasks"], self.launch),
        )
        # # Add "vocabularies/" route
        # rules.append(
        #     route("GET", routes["all"], self.get_all),
        # )
        # return rules

    # @request_search_args
    # @response_handler(many=True)
    # def get_all(self):
    #     """Return information about _all_ vocabularies."""
    #     config = current_service.config
    #     vocabtypeservice = VocabularyTypeService(config)
    #     identity = g.identity
    #     hits = vocabtypeservice.search(identity)

    #     return hits.to_dict(), 200

    @request_search_args
    @request_view_args
    @response_handler(many=True)
    def search(self):
        """Perform a search over the items."""
        hits = self.service.search(
            identity=g.identity,
            params=resource_requestctx.args,
            type=resource_requestctx.view_args["type"],
            search_preference=search_preference(),
        )
        return hits.to_dict(), 200

    @request_view_args
    @request_data
    @response_handler()
    def create(self):
        """Create an item."""
        item = self.service.create(
            g.identity,
            resource_requestctx.data or {},
        )
        return item.to_dict(), 201

    @request_view_args
    @response_handler()
    def read(self):
        """Read an item."""
        pid_value = (
            resource_requestctx.view_args["type"],
            resource_requestctx.view_args["pid_value"],
        )
        item = self.service.read(g.identity, pid_value)
        return item.to_dict(), 200

    @request_headers
    @request_view_args
    @request_data
    @response_handler()
    def update(self):
        """Update an item."""
        pid_value = (
            resource_requestctx.view_args["type"],
            resource_requestctx.view_args["pid_value"],
        )
        item = self.service.update(
            g.identity,
            pid_value,
            resource_requestctx.data,
            revision_id=resource_requestctx.headers.get("if_match"),
        )
        return item.to_dict(), 200

    @request_headers
    @request_view_args
    def delete(self):
        """Delete an item."""
        pid_value = (
            resource_requestctx.view_args["type"],
            resource_requestctx.view_args["pid_value"],
        )
        self.service.delete(
            g.identity,
            pid_value,
            revision_id=resource_requestctx.headers.get("if_match"),
        )
        return "", 204

    @request_data
    def launch(self):
        """Create a task."""
        self.service.launch(g.identity, resource_requestctx.data or {})
        return "", 202


class VocabulariesAdminResource(RecordResource):
    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        rules = super().create_url_rules()

        rules.append(
            route("GET", routes["list"], self.get_all_vocabulary_types),
        )
        return rules

    @request_search_args
    @response_handler(many=True)
    def get_all_vocabulary_types(self):
        """Return information about _all_ vocabularies."""
        config = current_service.config
        vocabtypeservice = VocabularyTypeService(config)
        identity = g.identity
        hits = vocabtypeservice.search(identity)

        return hits.to_dict(), 200
