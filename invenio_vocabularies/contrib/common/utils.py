# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Utility functions for Invenio-Vocabularies HTTP operations."""

from flask import current_app, has_app_context


def invenio_user_agent(default="Invenio"):
    """Return a User-Agent string, using Flask config if available."""
    if has_app_context():
        hostname = current_app.config.get("SITE_HOSTNAME", default)
        ui_url = current_app.config.get("SITE_UI_URL", None)
        return f"{hostname} (+{ui_url})" if ui_url else hostname
    return default
