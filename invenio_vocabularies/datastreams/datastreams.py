# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Base data stream."""

from flask import current_app

from .errors import ReaderError, TransformerError, WriterError


class StreamEntry:
    """Object to encapsulate streams processing."""

    def __init__(self, entry, record=None, errors=None, op_type=None, exc=None):
        """Constructor for the StreamEntry class.

        :param entry (object): The entry object, usually a record dict.
        :param record (object): The record object, usually a record class.
        :param errors (list, optional): List of errors. Defaults to None.
        :param op_type (str, optional): The operation type. Defaults to None.
        :param exc (str, optional): The raised unhandled exception. Defaults to None.
        """
        self.entry = entry
        self.record = record
        self.filtered = False
        self.errors = errors or []
        self.op_type = op_type
        self.exc = exc

    def log_errors(self, logger=None):
        """Log the errors using the provided logger or the default logger.

        :param logger (logging.Logger, optional): Logger instance to use. Defaults to None.
        """
        if logger is None:
            logger = current_app.logger
        for error in self.errors:
            logger.error(f"Error in entry {self.entry}: {error}")
        if self.exc:
            logger.error(f"Exception in entry {self.entry}: {self.exc}")


class DataStream:
    """Data stream."""

    def __init__(
        self,
        readers,
        writers,
        transformers=None,
        batch_size=100,
        write_many=False,
        *args,
        **kwargs,
    ):
        """Constructor.

        :param readers: an ordered list of readers.
        :param writers: an ordered list of writers.
        :param transformers: an ordered list of transformers to apply.
        """
        self._readers = readers
        self._transformers = transformers
        self._writers = writers
        self.batch_size = batch_size
        self.write_many = write_many

    def filter(self, stream_entry, *args, **kwargs):
        """Checks if an stream_entry should be filtered out (skipped)."""
        current_app.logger.debug(f"Filtering entry: {stream_entry.entry}")
        return False

    def process_batch(self, batch):
        """Process a batch of entries."""
        current_app.logger.info(f"Processing batch of size: {len(batch)}")
        transformed_entries = []
        for stream_entry in batch:
            if stream_entry.errors:
                current_app.logger.warning(
                    f"Skipping entry with errors: {stream_entry.errors}"
                )
                yield stream_entry  # reading errors
            else:
                transformed_entry = self.transform(stream_entry)
                if transformed_entry.errors:
                    yield transformed_entry
                elif self.filter(transformed_entry):
                    transformed_entry.filtered = True
                    yield transformed_entry
                else:
                    transformed_entries.append(transformed_entry)
        if transformed_entries:
            if self.write_many:
                yield from self.batch_write(transformed_entries)
            else:
                yield from (self.write(entry) for entry in transformed_entries)

    def process(self, *args, **kwargs):
        """Iterates over the entries.

        Uses the reader to get the raw entries and transforms them.
        It will iterate over the `StreamEntry` objects returned by
        the reader, apply the transformations and yield the result of
        writing it.
        """
        current_app.logger.info("Starting data stream processing")
        batch = []
        for stream_entry in self.read():
            batch.append(stream_entry)
            if len(batch) >= self.batch_size:
                current_app.logger.debug(f"Processing batch of size: {len(batch)}")
                yield from self.process_batch(batch)
                batch = []

        # Process any remaining entries in the last batch
        if batch:
            current_app.logger.debug(f"Processing final batch of size: {len(batch)}")
            yield from self.process_batch(batch)

    def read(self):
        """Recursively read the entries."""
        current_app.logger.debug("Reading entries from readers")

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
                    current_app.logger.error(f"Reader error: {str(err)}")
                    yield StreamEntry(
                        entry=item,
                        errors=[f"{current_gen_func.__qualname__}: {str(err)}"],
                    )

        read_gens = [r.read for r in self._readers]
        yield from pipe_gen(read_gens)

    def transform(self, stream_entry, *args, **kwargs):
        """Apply the transformations to an stream_entry."""
        current_app.logger.debug(f"Transforming entry: {stream_entry.entry}")
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
        current_app.logger.debug(f"Writing entry: {stream_entry.entry}")
        for writer in self._writers:
            try:
                writer.write(stream_entry)
            except WriterError as err:
                current_app.logger.error(f"Writer error: {str(err)}")
                stream_entry.errors.append(f"{writer.__class__.__name__}: {str(err)}")

        return stream_entry

    def batch_write(self, stream_entries, *args, **kwargs):
        """Apply the transformations to an stream_entry. Errors are handler in the service layer."""
        current_app.logger.debug(f"Batch writing entries: {len(stream_entries)}")
        for writer in self._writers:
            yield from writer.write_many(stream_entries)

    def total(self, *args, **kwargs):
        """The total of entries obtained from the origin."""
        raise NotImplementedError()
