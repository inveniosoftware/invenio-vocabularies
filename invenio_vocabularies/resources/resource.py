# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary resource."""

from functools import wraps

from flask_resources.context import resource_requestctx
from flask_resources.parsers import URLArgsParser
from flask_resources.serializers import MarshmallowJSONSerializer
from invenio_records_resources.resources import ItemLinksSchema, \
    RecordResource, RecordResourceConfig, RecordResponse, SearchLinksSchema, \
    search_link_params
from invenio_records_resources.resources.records.schemas_url_args import \
    SearchURLArgsSchema
from marshmallow import fields

from .serializer import VocabularyL10NItemSchema, VocabularyL10NListSchema


def item_link_params(record):
    """Create URITemplate variables for item links."""
    return {
        'pid_value': record.pid.pid_value,
        'vocabulary_type': record.type.id,
    }


def search_link_params(page_offset):
    """Create URITemplate variables for search links."""
    def _inner(search_dict):
        # Filter out internal parameters
        params = {
            k: v for k, v in search_dict.items() if not k.startswith('_')
        }
        params['page'] += page_offset
        return {
            'params': params,
            'vocabulary_type': search_dict['_type'].id
        }
    return _inner


#
# URL args
#
class VocabularySearchURLArgsSchema(SearchURLArgsSchema):
    """Add parameter to parse tags."""

    tags = fields.Str()


#
# Resource config
#
class VocabulariesResourceConfig(RecordResourceConfig):
    """Vocabulary resource configuration."""

    list_route = '/vocabularies/<vocabulary_type>'
    item_route = f'{list_route}/<pid_value>'

    request_url_args_parser = {
        "search": URLArgsParser(VocabularySearchURLArgsSchema)
    }

    links_config = {
        "record": ItemLinksSchema.create(
            template='/api/vocabularies/{vocabulary_type}/{pid_value}',
            params=item_link_params,
        ),
        "search": SearchLinksSchema.create(
            template='/api/vocabularies/{vocabulary_type}{?params*}',
            params_func=search_link_params,
        ),
    }

    response_handlers = {
        **RecordResourceConfig.response_handlers,
        'application/vnd.inveniordm.v1+json': RecordResponse(
            MarshmallowJSONSerializer(
                item_schema=VocabularyL10NItemSchema,
                list_schema=VocabularyL10NListSchema,
            )
        )
    }


#
# Resource definition
#
def list_route(f):
    """Decorator for list routes to inject the vocabulary type."""
    @wraps(f)
    def inner(*args, **kwargs):
        resource_requestctx.url_args["type"] = \
            resource_requestctx.route["vocabulary_type"],
        return f(*args, **kwargs)
    return inner


def item_route(f):
    """Decorator for item routes to inject the vocabulary type."""
    @wraps(f)
    def inner(*args, **kwars):
        resource_requestctx.route["pid_value"] = (
            resource_requestctx.route["vocabulary_type"],
            resource_requestctx.route["pid_value"]
        )
        return f(*args, **kwars)
    return inner


class VocabulariesResource(RecordResource):
    """Custom record resource"."""

    @item_route
    def read(self):
        """Read an item."""
        return super().read()

    @item_route
    def delete(self):
        """Delete an item."""
        return super().delete()

    @item_route
    def update(self):
        """Update an item."""
        return super().update()

    @list_route
    def search(self):
        """Perform a search over the items."""
        return super().search()
