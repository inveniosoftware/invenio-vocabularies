# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Data Streams Celery tasks."""

from celery import shared_task
from invenio_logging.structlog import LoggerFactory

from ..datastreams import StreamEntry
from ..datastreams.factories import WriterFactory


@shared_task(ignore_result=True, logger=None)
def write_entry(writer_config, entry):
    """Write an entry.

    :param writer: writer configuration as accepted by the WriterFactory.
    :param entry: dictionary, StreamEntry is not serializable.
    """
    if not logger:
        logger = LoggerFactory.get_logger("write_entry")
    writer = WriterFactory.create(config=writer_config)
    stream_entry_processed = writer.write(StreamEntry(entry))
    if stream_entry_processed.errors:
        logger.error("Error writing entry", entry=entry, errors=stream_entry_processed.errors)
    else:
        logger.info("Entry written", entry=entry)

@shared_task(ignore_result=True)
def write_many_entry(writer_config, entries, logger=None):
    """Write many entries.

    :param writer: writer configuration as accepted by the WriterFactory.
    :param entry: lisf ot dictionaries, StreamEntry is not serializable.
    """
    if not logger:
        logger = LoggerFactory.get_logger("write_many_entry")
    writer = WriterFactory.create(config=writer_config)
    stream_entries = [StreamEntry(entry) for entry in entries]
    stream_entries_processed = writer.write_many(stream_entries)
    errored = [entry for entry in stream_entries_processed if entry.errors]
    succeeded = len(stream_entries_processed) - len(errored)
    logger.info("Entries written", succeeded=succeeded)
    if errored:
        for entry in errored:
            logger.error("Error writing entry", entry=entry.entry, errors=entry.errors)
