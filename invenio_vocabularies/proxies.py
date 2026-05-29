# SPDX-FileCopyrightText: 2021-2024 CERN.
# SPDX-FileCopyrightText: 2021 Northwestern University.
# SPDX-License-Identifier: MIT

"""Proxies to the service and resource."""

from flask import current_app
from werkzeug.local import LocalProxy


def _ext_proxy(attr):
    return LocalProxy(
        lambda: getattr(current_app.extensions["invenio-vocabularies"], attr)
    )


current_service = _ext_proxy("vocabularies_service")
"""Proxy to the instantiated vocabulary service."""


current_resource = _ext_proxy("resource")
"""Proxy to the instantiated vocabulary resource."""
