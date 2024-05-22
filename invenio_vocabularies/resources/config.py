# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Vocabularies is free software; you can redistringibute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Resources config."""

import marshmallow as ma
from flask_resources import HTTPJSONException, ResourceConfig, create_error_handler
from invenio_records_resources.resources.errors import ErrorHandlersMixin
from invenio_records_resources.resources.records.args import SearchRequestArgsSchema
from invenio_records_resources.services.base.config import ConfiguratorMixin


class TasksResourceConfig(ResourceConfig, ConfiguratorMixin):
    """Celery tasks resource config."""

    # Blueprint configuration
    blueprint_name = "tasks"
    url_prefix = "/tasks"
    routes = {"list": ""}


class VocabulariesSearchRequestArgsSchema(SearchRequestArgsSchema):
    """Vocabularies search request parameters."""

    active = ma.fields.Boolean()


class VocabulariesResourceConfig(ResourceConfig, ConfiguratorMixin):
    """Vocabularies resource config."""

    # /vocabulary - all
    # Blueprint configuration
    blueprint_name = "vocabularies"
    url_prefix = "/vocabularies"
    routes = {
        "list": "",
        "item": "/<vocabulary_id>",
    }

    # Request parsing
    request_read_args = {}
    request_view_args = {"vocabulary_id": ma.fields.String}
    request_search_args = VocabulariesSearchRequestArgsSchema

    error_handlers = {
        **ErrorHandlersMixin.error_handlers,
        # TODO: Add custom error handlers here
    }


class VocabulariesSearchRequestArgsSchema(SearchRequestArgsSchema):
    """Vocabularies search request parameters."""

    status = ma.fields.Boolean()


class VocabularyTypeResourceConfig(ResourceConfig, ConfiguratorMixin):
    """Runs resource config."""

    # /vocabulary/vocabulary_id
    # Blueprint configuration
    blueprint_name = "vocabulary_runs"
    url_prefix = ""

    routes = {
        "all": "/",
        "list": "/vocabularies/<vocabulary_id>",
        "item": "/vocabularies/<vocabulary_id>/<vocabulary_type_id>",
    }

    # Request parsing
    request_view_args = {
        "vocabulary_id": ma.fields.String,
        "vocabulary_type_id": ma.fields.String,
    }

    request_search_args = VocabulariesSearchRequestArgsSchema

    error_handlers = {
        **ErrorHandlersMixin.error_handlers,
        # TODO: Add custom error handlers here
    }
