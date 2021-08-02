# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Subjects services."""


class SubjectsLabels:
    """Fetching of subjects labels for facets."""

    def __call__(self, ids):
        """Return the mapping when evaluated.

        For subjects, the ids received are actually human-readable and coming
        from subject and scheme. So we use them as-is!
        """
        unique_ids = list(set(ids))
        return {id_: id_ for id_ in unique_ids}
