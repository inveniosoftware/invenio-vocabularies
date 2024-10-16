# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#

"""Vocabulary generators."""

from invenio_access import any_user, authenticated_user
from invenio_records_permissions.generators import Generator
from invenio_search.engine import dsl


class IfTags(Generator):
    """Generator to filter based on tags.

    This generator will filter records based on the tags field.
    Optionally, it can be configured to only allow authenticated users.
    """

    def __init__(self, include=None, exclude=None, only_authenticated=False):
        """Constructor."""
        self.include = include or []
        self.exclude = exclude or []
        self.only_authenticated = only_authenticated

    def needs(self, **kwargs):
        """Enabling Needs."""
        return [authenticated_user] if self.only_authenticated else [any_user]

    def query_filter(self, **kwargs):
        """Search based on configured tags."""
        must_clauses = []
        must_not_clauses = []

        if self.include:
            must_clauses.append(dsl.Q("terms", tags=self.include))

        if self.exclude:
            must_not_clauses.append(dsl.Q("terms", tags=self.exclude))

        return dsl.Q(
            "bool",
            must=must_clauses,
            must_not=must_not_clauses,
        )
