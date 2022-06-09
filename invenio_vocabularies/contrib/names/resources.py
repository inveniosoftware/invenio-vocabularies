# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names vocabulary resources."""

from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources.records.resource import request_view_args
from marshmallow import fields

from .names import record_type


class NamesResourceConfig(record_type.resource_config_cls):
    """Name resource."""

    routes = record_type.resource_config_cls.routes
    routes["item-names-resolve"] = "/<pid_type>/<pid_value>"
    request_view_args = {
        "pid_value": fields.Str(),
        "pid_type": fields.Str(),
    }


class NamesResource(record_type.resource_cls):
    """Name resource."""

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes
        url_rules = super(NamesResource, self).create_url_rules()
        url_rules += [
            route("GET", routes["item-names-resolve"], self.name_resolve_by_id),
        ]

        return url_rules

    @request_view_args
    @response_handler()
    def name_resolve_by_id(self):
        """Resolve an identifier."""
        item = self.service.resolve(
            id_=resource_requestctx.view_args["pid_value"],
            id_type=resource_requestctx.view_args["pid_type"],
            identity=g.identity,
        )

        return item.to_dict(), 200
