# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio module for managing vocabularies."""

from . import config
from .resources.records.resource import VocabulariesResource, \
    VocabulariesResourceConfig
from .services.records.service import VocabulariesService, \
    VocabulariesServiceConfig


class InvenioVocabularies(object):
    """Invenio-Vocabularies extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        self.resource = None
        self.service = None
        if app:
            self.init_app(app)

    def init_resource(self, app):
        """Initialize vocabulary resources."""
        # The config must be overwritable by an instance, hence we use this
        # pattern
        self.service = VocabulariesService(
            config=app.config["VOCABULARIES_SERVICE_CONFIG"],
        )
        self.resource = VocabulariesResource(
            service=self.service,
            config=app.config["VOCABULARIES_RESOURCE_CONFIG"],
        )

    def init_app(self, app):
        """Flask application initialization."""
        app.extensions["invenio-vocabularies"] = self
        self.init_config(app)
        self.init_resource(app)

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault(
            "VOCABULARIES_RESOURCE",
            VocabulariesResource,
        )
        app.config.setdefault(
            "VOCABULARIES_SERVICE",
            VocabulariesService,
        )
        for k in dir(config):
            if k.startswith("VOCABULARIES_"):
                app.config.setdefault(k, getattr(config, k))
