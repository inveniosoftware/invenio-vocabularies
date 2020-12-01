# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary API views."""

from invenio_vocabularies.records.resource import VocabularyResource, VocabularyResourceConfig
from invenio_vocabularies.records.service import ServiceConfig, Service


def create_blueprints(app):
    """."""
    name = "invenio_vocabularies"
    resource = VocabularyResource(
        config=VocabularyResourceConfig,
        service=Service(config=ServiceConfig)
    )
    return resource.as_blueprint(name)
