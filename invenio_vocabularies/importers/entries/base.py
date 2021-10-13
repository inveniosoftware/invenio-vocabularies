# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary entries."""

from ..tasks import create_vocabulary_record


class BaseEntry:
    """Loading vocabulary superclass."""

    def __init__(self, service_str, directory, id_, entry):
        """Constructor."""
        self._dir = directory
        self._id = id_
        self._entry = entry
        self.service_str = service_str

    def load(self, identity, ignore=None, delay=False):
        """Template method design pattern for loading entries."""
        ignore = ignore or set()
        self.pre_load(identity, ignore=ignore)
        for data in self.iterate(ignore=ignore):
            self.create_record(data, delay=delay)
        return self.loaded()

    def create_record(self, data, delay=False):
        """Create the record."""
        if delay:
            create_vocabulary_record.delay(self.service_str, data)
        else:  # mostly for tests
            create_vocabulary_record(self.service_str, data)
