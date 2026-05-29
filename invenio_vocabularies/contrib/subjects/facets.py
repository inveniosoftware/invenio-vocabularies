# SPDX-FileCopyrightText: 2021 Northwestern University.
# SPDX-License-Identifier: MIT

"""Subjects services."""


class SubjectsLabels:
    """Fetching of subjects labels for facets."""

    def __call__(self, ids):
        """Return the mapping when evaluated.

        In this case, the ids received are actually the vocabulary `scheme`
        (top-level) and `subject` (nested). And since they are already
        human-readable, we keep them as-is.
        """
        unique_ids = list(set(ids))
        return {id_: id_ for id_ in unique_ids}
