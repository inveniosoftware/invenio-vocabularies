# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Data Streams Celery tasks."""

from celery import shared_task

from ..datastreams import StreamEntry
from ..datastreams.factories import WriterFactory


@shared_task(ignore_result=True)
def write_entry(writer_config, entry):
    """Write an entry.

    :param writer: writer configuration as accepted by the WriterFactory.
    :param entry: dictionary, StreamEntry is not serializable.
    """
    writer = WriterFactory.create(config=writer_config)
    writer.write(StreamEntry(entry))


@shared_task(ignore_result=True)
def write_many_entry(writer_config, entries):
    """Write many entries.

    :param writer: writer configuration as accepted by the WriterFactory.
    :param entry: lisf ot dictionaries, StreamEntry is not serializable.
    """
    writer = WriterFactory.create(config=writer_config)
    stream_entries = [StreamEntry(entry) for entry in entries]
    writer.write_many(stream_entries)
