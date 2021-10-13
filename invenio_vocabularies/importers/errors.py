# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Importer errors."""


class ConflictingOriginError(Exception):
    """Exception when multiple modules provide same vocabulary type."""

    def __init__(self, errors):
        """Constructor."""
        message = "\n".join(errors)
        super().__init__(message)
        self.errors = errors
