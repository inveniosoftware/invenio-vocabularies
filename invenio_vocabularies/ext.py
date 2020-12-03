# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio module for managing vocabularies."""

from flask_babelex import gettext as _

from . import config
from .resources.records.resource import VocabularyResource, \
    VocabularyResourceConfig
from .services.records.service import Service, ServiceConfig


class InvenioVocabularies(object):
    """Invenio-Vocabularies extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        resource = VocabularyResource(
            config=VocabularyResourceConfig,
            service=Service(config=ServiceConfig),
        )
        app.register_blueprint(resource.as_blueprint("vocabularies_types"))
        app.extensions["invenio-vocabularies"] = self

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("VOCABULARIES_"):
                app.config.setdefault(k, getattr(config, k))
