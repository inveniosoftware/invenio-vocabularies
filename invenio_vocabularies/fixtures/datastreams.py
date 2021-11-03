# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Base data stream."""

from .errors import TransformerError, WriterError


class StreamResult:
    """Result object for streams processing."""

    def __init__(self, entry, errors=None):
        """Constructor."""
        self.entry = entry
        self.errors = errors or []


class BaseDataStream:
    """Base data stream."""

    def __init__(self, reader, writers, transformers=None, *args, **kwargs):
        """Constructor.

        :param reader: the reader object.
        :param writers: an ordered list of writers.
        :param transformers: an ordered list of transformers to apply.
        """
        self._reader = reader  # a single entry point
        self._transformers = transformers
        self._writers = writers

    def filter(self, entry, *args, **kwargs):
        """Checks if an entry should be filtered out (skipped)."""
        return False

    def process(self, *args, **kwargs):
        """Iterates over the entries.

        Uses the reader to get the raw entries and transforms them.
        """
        for entry in self._reader.read():
            result = self.transform(entry)
            if result.errors:
                yield StreamResult(entry=entry, errors=result.errors)
            elif not self.filter(result.entry):
                yield self.write(result.entry)

    def transform(self, entry, *args, **kwargs):
        """Apply the transformations to an entry."""
        for transformer in self._transformers:
            try:
                entry = transformer.apply(entry)
            except TransformerError as err:
                return StreamResult(
                    entry,
                    # FIXME: __ is ugly, add name cls attr?
                    [f"{transformer.__class__.__name__}: {str(err)}"]
                )

        return StreamResult(entry)

    def write(self, entry, *args, **kwargs):
        """Apply the transformations to an entry."""
        errors = []
        for writer in self._writers:
            try:
                writer.write(entry)
            except WriterError as err:
                # FIXME: __ is ugly, add name cls attr?
                errors.append(f"{writer.__class__.__name__}: {str(err)}")

        return StreamResult(entry, errors)

    def total(self, *args, **kwargs):
        """The total of entries obtained from the origin."""
        pass
