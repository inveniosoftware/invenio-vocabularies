# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 California Institute of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary ror configuration."""

from flask import current_app
from werkzeug.local import LocalProxy

funder_schemes = LocalProxy(lambda: current_app.config["VOCABULARIES_FUNDER_SCHEMES"])

funder_fundref_doi_prefix = LocalProxy(
    lambda: current_app.config["VOCABULARIES_FUNDER_DOI_PREFIX"]
)
