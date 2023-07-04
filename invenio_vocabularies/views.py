# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio vocabularies views."""

from flask import Blueprint

blueprint = Blueprint("invenio_vocabularies_ext", __name__)


@blueprint.record_once
def init(state):
    """Init app."""
    app = state.app
    # Register services - cannot be done in extension because
    # Invenio-Records-Resources might not have been initialized.
    sregistry = app.extensions["invenio-records-resources"].registry
    ext = app.extensions["invenio-vocabularies"]
    sregistry.register(ext.affiliations_service, service_id="affiliations")
    sregistry.register(ext.awards_service, service_id="awards")
    sregistry.register(ext.funders_service, service_id="funders")
    sregistry.register(ext.names_service, service_id="names")
    sregistry.register(ext.subjects_service, service_id="subjects")
    sregistry.register(ext.service, service_id="vocabularies")
    # Register indexers
    iregistry = app.extensions["invenio-indexer"].registry
    iregistry.register(ext.affiliations_service.indexer, indexer_id="affiliations")
    iregistry.register(ext.awards_service.indexer, indexer_id="awards")
    iregistry.register(ext.funders_service.indexer, indexer_id="funders")
    iregistry.register(ext.names_service.indexer, indexer_id="names")
    iregistry.register(ext.subjects_service.indexer, indexer_id="subjects")
    iregistry.register(ext.service.indexer, indexer_id="vocabularies")


def create_blueprint_from_app(app):
    """Create app blueprint."""
    return app.extensions["invenio-vocabularies"].resource.as_blueprint()


def create_affiliations_blueprint_from_app(app):
    """Create app blueprint."""
    return app.extensions["invenio-vocabularies"].affiliations_resource.as_blueprint()


def create_awards_blueprint_from_app(app):
    """Create app blueprint."""
    return app.extensions["invenio-vocabularies"].awards_resource.as_blueprint()


def create_funders_blueprint_from_app(app):
    """Create app blueprint."""
    return app.extensions["invenio-vocabularies"].funders_resource.as_blueprint()


def create_names_blueprint_from_app(app):
    """Create app blueprint."""
    return app.extensions["invenio-vocabularies"].names_resource.as_blueprint()


def create_subjects_blueprint_from_app(app):
    """Create app blueprint."""
    return app.extensions["invenio-vocabularies"].subjects_resource.as_blueprint()
