# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Local importer."""

import yaml

from .entries import Entry, NestedEntry


class LocalImporter:
    """Vocabularies fixture.

    This class' responsibility is to load the vocabularies in its
    vocabularies file.
    """

    def __init__(self, identity, filepath, delay=True):
        """Initialize the fixture."""
        self._identity = identity
        self._filepath = filepath
        self._delay = delay

    def read(self):
        """Return content of vocabularies file."""
        dir_ = self._filepath.parent
        with open(self._filepath) as f:
            data = yaml.safe_load(f) or {}
            for id_, yaml_entry in data.items():
                # Some vocabularies are non-generic
                if id_ == "subjects":
                    entry = NestedEntry(
                        "subjects_service", dir_, id_, yaml_entry
                    )
                elif id_ == "affiliations":
                    entry = NestedEntry(
                        "affiliations_service", dir_, id_, yaml_entry
                    )
                else:
                    entry = Entry(dir_, id_, yaml_entry)

                yield id_, entry

    def get_records_by_vocabulary(self, vocabulary_id):
        """Get all records of a given vocabulary."""
        for id_, entry in self.read():
            if vocabulary_id != id_:
                continue
            for data in entry.iterate(set()):
                yield data

    def load(self, ignore=None):
        """Load the whole fixture.

        ignore: iterable of ids to ignore

        For subjects (or any vocabulary with a dict of data-file), the id
        that counts is ``<vocabulary id>.<dict key>``.

        Returns all vocabulary ids loaded so far.
        """
        ids = set().union(ignore) if ignore else set()

        for id_, entry in self.read():
            ids.update(
                entry.load(self._identity, ignore=ids, delay=self._delay)
            )

        return ids
