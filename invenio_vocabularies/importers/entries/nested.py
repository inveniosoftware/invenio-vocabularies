# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary entry with schemes."""

from invenio_db import db

from ...records.models import VocabularyScheme
from ..iterators import create_iterator
from .base import BaseEntry


class NestedEntry(BaseEntry):
    """Vocabulary fixture for specific vocabulary with schemes."""

    def __init__(self, service_str, directory, id_, entry):
        """Constructor."""
        super().__init__(service_str, directory, id_, entry)
        self._loaded = []

    # Template methods
    def pre_load(self, identity, ignore):
        """Actions taken before iteratively creating records."""
        for scheme in self.schemes():
            id_ = f"{self._id}.{scheme['id']}"
            if id_ not in ignore:
                self.create_scheme(scheme)

    def iterate(self, ignore):
        """Iterate over dicts of file content."""
        self._loaded = []

        for scheme in self.schemes():
            id_ = f"{self._id}.{scheme['id']}"
            if id_ not in ignore:
                self._loaded.append(id_)
                filepath = self._dir / scheme.get("data-file")
                yield from create_iterator(filepath)

    def loaded(self):
        """Vocabularies actually loaded."""
        return self._loaded

    # Other interface methods
    @property
    def covered_ids(self):
        """List of ids of the subvocabularies covered by this entry."""
        return [f"{s['id']}" for s in self.schemes()]

    # Helpers
    def schemes(self):
        """Return schemes."""
        return self._entry.get("schemes", [])

    def create_scheme(self, metadata):
        """Create the vocabulary scheme row."""
        # FIXME: do in service like create_type
        id_ = metadata["id"]
        name = metadata.get("name", "")
        uri = metadata.get("uri", "")
        VocabularyScheme.create(
            id=id_, parent_id=self._id, name=name, uri=uri)
        db.session.commit()
