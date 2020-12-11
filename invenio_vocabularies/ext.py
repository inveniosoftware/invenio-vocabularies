# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio module for managing vocabularies."""

from . import config
from .resources.resource import VocabulariesResource
from .services.service import VocabulariesService


class InvenioVocabularies(object):
    """Invenio-Vocabularies extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        self.resource = None
        self.service = None
        self.subjects_service = None
        self.subjects_resource = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.init_resource(app)
        app.extensions["invenio-vocabularies"] = self

    def init_resource(self, app):
        """Initialize vocabulary resources."""
        self.service = VocabulariesService(
            config=app.config["VOCABULARIES_SERVICE_CONFIG"],
        )
        self.resource = VocabulariesResource(
            service=self.service,
            config=app.config["VOCABULARIES_RESOURCE_CONFIG"],
        )

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("VOCABULARIES_"):
                app.config.setdefault(k, getattr(config, k))
