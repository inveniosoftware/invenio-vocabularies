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
def write_entry(writer, entry):
    """Write an entry.

    :param writer: writer configuration as accepted by the WriterFactory.
    :param entry: dictionary, StreamEntry is not serializable.
    """
    writer = WriterFactory.create(config=writer)
    writer.write(StreamEntry(entry))
