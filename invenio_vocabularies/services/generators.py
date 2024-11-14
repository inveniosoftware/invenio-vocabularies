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
from invenio_records_permissions.generators import ConditionalGenerator
from invenio_search.engine import dsl


class IfTags(ConditionalGenerator):
    """Generator to filter based on tags.

    This generator will filter out records based on the tags field.
    """

    def __init__(self, tags, then_, else_):
        """Constructor."""
        self.tags = tags or []
        super().__init__(then_, else_)

    def _condition(self, record=None, **kwargs):
        """Check if the record has the tags."""
        return any(tag in record.get("tags", []) for tag in self.tags)

    def query_filter(self, **kwargs):
        """Search based on configured tags."""
        must_not_clauses = [dsl.Q("terms", tags=self.tags)]
        return dsl.Q(
            "bool",
            must_not=must_not_clauses,
        )
