# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Utility functions for Invenio-Vocabularies HTTP operations."""

from flask import current_app, has_app_context


def invenio_user_agent(default="Invenio"):
    """Return a User-Agent string, using Flask config if available."""
    if has_app_context():
        hostname = current_app.config.get("SITE_HOSTNAME", default)
        ui_url = current_app.config.get("SITE_UI_URL", None)
        return f"{hostname} (+{ui_url})" if ui_url else hostname
    return default
