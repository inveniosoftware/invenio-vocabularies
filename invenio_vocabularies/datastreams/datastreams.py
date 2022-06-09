# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Base data stream."""

from .errors import ReaderError, TransformerError, WriterError


class StreamEntry:
    """Object to encapsulate streams processing."""

    def __init__(self, entry, errors=None):
        """Constructor."""
        self.entry = entry
        self.filtered = False
        self.errors = errors or []


class DataStream:
    """Data stream."""

    def __init__(self, readers, writers, transformers=None, *args, **kwargs):
        """Constructor.

        :param readers: an ordered list of readers.
        :param writers: an ordered list of writers.
        :param transformers: an ordered list of transformers to apply.
        """
        self._readers = readers
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
        for stream_entry in self.read():
            if stream_entry.errors:
                yield stream_entry  # reading errors
            else:
                transformed_entry = self.transform(stream_entry)
                if transformed_entry.errors:
                    yield transformed_entry
                elif self.filter(transformed_entry):
                    transformed_entry.filtered = True
                    yield transformed_entry
                else:
                    yield self.write(transformed_entry)

    def read(self):
        """Recursively read the entries."""

        def pipe_gen(gen_funcs, piped_item=None):
            _gen_funcs = list(gen_funcs)  # copy to avoid modifying ref list
            # use and remove the current generator
            current_gen_func = _gen_funcs.pop(0)
            for item in current_gen_func(piped_item):
                try:
                    # exhaust iterations of subsequent generators
                    if _gen_funcs:
                        yield from pipe_gen(_gen_funcs, piped_item=item)
                    # there is no subsequent generator, return the current item
                    else:
                        yield StreamEntry(item)
                except ReaderError as err:
                    yield StreamEntry(
                        entry=item,
                        errors=[f"{current_gen_func.__qualname__}: {str(err)}"],
                    )

        read_gens = [r.read for r in self._readers]
        yield from pipe_gen(read_gens)

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
                stream_entry.errors.append(f"{writer.__class__.__name__}: {str(err)}")

        return stream_entry

    def total(self, *args, **kwargs):
        """The total of entries obtained from the origin."""
        raise NotImplementedError()
