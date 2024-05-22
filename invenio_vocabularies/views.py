# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio vocabularies views."""

from flask import Blueprint

blueprint = Blueprint(
    "invenio_vocabularies_ext", __name__, template_folder="./templates"
)


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


def create_list_blueprint_from_app(app):
    """Create app blueprint."""
    return app.extensions[
        "invenio-vocabularies"
    ].vocabulary_admin_resource.as_blueprint()
