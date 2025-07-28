# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Data Streams Celery tasks."""

from celery import shared_task
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_jobs.logging.jobs import EMPTY_JOB_CTX, job_context
from invenio_jobs.proxies import current_runs_service

from ..datastreams import StreamEntry
from ..datastreams.factories import WriterFactory


@shared_task(ignore_result=True)
def write_entry(writer_config, entry, subtask_run_id=None):
    """Write an entry.

    :param writer: writer configuration as accepted by the WriterFactory.
    :param entry: dictionary, StreamEntry is not serializable.
    """
    job_ctx = job_context.get()
    job_id = job_ctx.get("job_id", None) if job_ctx is not EMPTY_JOB_CTX else None
    if subtask_run_id and job_id:
        subtask_run = current_runs_service.get(
            system_identity, job_id=job_id, run_id=subtask_run_id
        )
        current_runs_service.start_processing_subtask(
            system_identity, subtask_run.id, job_id=job_id
        )

    writer = WriterFactory.create(config=writer_config)
    try:
        processed_stream_entry = writer.write(StreamEntry(entry))
        errored_entries_count = 1 if processed_stream_entry.errors else 0
        if subtask_run_id and job_id:
            current_runs_service.finalize_subtask(
                system_identity,
                subtask_run_id,
                job_id,
                success=True if not processed_stream_entry.errors else False,
                errored_entries_count=errored_entries_count,
            )
    except Exception as exc:
        current_app.logger.error(f"Error writing entry {entry}: {exc}")
        if subtask_run_id and job_id:
            current_runs_service.finalize_subtask(
                system_identity,
                subtask_run_id,
                job_id,
                success=False,
                errored_entries_count=1,
            )


@shared_task(ignore_result=True)
def write_many_entry(writer_config, entries, subtask_run_id=None):
    """Write many entries.

    :param writer: writer configuration as accepted by the WriterFactory.
    :param entry: lisf ot dictionaries, StreamEntry is not serializable.
    """
    job_ctx = job_context.get()
    job_id = job_ctx.get("job_id", None) if job_ctx is not EMPTY_JOB_CTX else None
    if subtask_run_id and job_id:
        subtask_run = current_runs_service.get(
            system_identity, job_id=job_id, run_id=subtask_run_id
        )
        current_runs_service.start_processing_subtask(
            system_identity, subtask_run.id, job_id=job_id
        )
    writer = WriterFactory.create(config=writer_config)
    stream_entries = [StreamEntry(entry) for entry in entries]
    try:
        processed_stream_entries = writer.write_many(stream_entries)
        errored_entries_count = sum(
            1 for entry in processed_stream_entries if entry.errors
        )
        if subtask_run_id and job_id:
            current_runs_service.finalize_subtask(
                system_identity,
                subtask_run_id,
                job_id,
                success=True,
                errored_entries_count=errored_entries_count,
            )
    except Exception as exc:
        current_app.logger.error(
            f"Error writing entries {entries}: {exc}. The errorred entries count might be incorrect as an entire batch might have failed"
        )
        if subtask_run_id and job_id:
            current_runs_service.finalize_subtask(
                system_identity,
                subtask_run_id,
                job_id,
                success=False,
            )
