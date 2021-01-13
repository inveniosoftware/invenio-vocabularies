# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Proxies to the service and resource."""

from flask import current_app
from werkzeug.local import LocalProxy


def _ext_proxy(attr):
    return LocalProxy(
        lambda: getattr(current_app.extensions['invenio-vocabularies'], attr))


current_service = _ext_proxy('service')
"""Proxy to the instantiated vocabulary service."""


current_resource = _ext_proxy('resource')
"""Proxy to the instantiated vocabulary resource."""
