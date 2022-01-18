# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Base data stream."""

from .errors import TransformerError, WriterError


class StreamEntry:
    """Object to encapsulate streams processing."""

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

    def filter(self, stream_entry, *args, **kwargs):
        """Checks if an stream_entry should be filtered out (skipped)."""
        return False

    def process(self, *args, **kwargs):
        """Iterates over the entries.

        Uses the reader to get the raw entries and transforms them.
        It will iterate over the `StreamEntry` objects returned by
        the reader, apply the transformations and yield the result of
        writing it.
        """
        for stream_entry in self._reader.read():
            transformed_entry = self.transform(stream_entry)
            if transformed_entry.errors:
                yield transformed_entry
            elif not self.filter(transformed_entry):
                yield self.write(transformed_entry)

    def transform(self, stream_entry, *args, **kwargs):
        """Apply the transformations to an stream_entry."""
        for transformer in self._transformers:
            try:
                stream_entry = transformer.apply(stream_entry)
            except TransformerError as err:
                stream_entry.errors.append(
                    f"{transformer.__class__.__name__}: {str(err)}"
                )
                return stream_entry  # break loop

        return stream_entry

    def write(self, stream_entry, *args, **kwargs):
        """Apply the transformations to an stream_entry."""
        for writer in self._writers:
            try:
                writer.write(stream_entry)
            except WriterError as err:
                stream_entry.errors.append(
                    f"{writer.__class__.__name__}: {str(err)}"
                )

        return stream_entry

    def total(self, *args, **kwargs):
        """The total of entries obtained from the origin."""
        pass
