# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary entries."""

from ...proxies import current_service
from ..iterators import create_iterator
from .base import BaseEntry


class Entry(BaseEntry):
    """Vocabulary fixture with single data-file."""

    def __init__(self, directory, id_, entry):
        """Constructor."""
        super().__init__("vocabulary_service", directory, id_, entry)

    # Template methods
    def pre_load(self, identity, ignore):
        """Actions taken before iteratively creating records."""
        if self._id not in ignore:
            pid_type = self._entry['pid-type']
            current_service.create_type(identity, self._id, pid_type)

    def iterate(self, ignore):
        """Iterate over dicts of file content."""
        if self._id not in ignore:
            filepath = self._dir / self._entry["data-file"]
            for data in create_iterator(filepath):
                data['type'] = self._id
                yield data

    def loaded(self):
        """Vocabularies actually loaded."""
        return [self._id]

    # Other interface methods
    @property
    def covered_ids(self):
        """Just the id of the vocabulary covered by this entry as a list."""
        return [self._id]
