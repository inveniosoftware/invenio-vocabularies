# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Jobs module."""

import datetime

from invenio_jobs.jobs import JobType

from invenio_vocabularies.services.tasks import process_datastream
from marshmallow import Schema, fields
from marshmallow_utils.fields import TZDateTime
from datetime import timezone


class ArgsSchema(Schema):

    since = TZDateTime(
        timezone=timezone.utc,
        format="iso",
        metadata={
            "description": "YYYY-MM-DD HH:mm format. Leave field empty if it should continue since last successful run"
        },
    )
    type = fields.String(
        metadata={"type": "hidden"},
        dump_default="ArgsSchemaAPI",
        load_default="ArgsSchemaAPI",
    )


class ProcessDataStreamJob(JobType):

    arguments_schema = ArgsSchema
    task = process_datastream
    id = "process_datastream"
    title = "Generic Process Data Stream task"

    @classmethod
    def build_task_arguments(cls, job_obj, since=None, custom_args=None, **kwargs):
        raise NotImplemented


class ProcessRORAffiliationsJob(ProcessDataStreamJob):
    """Process ROR affiliations datastream registered task."""

    description = "Process ROR affiliations"
    title = "Load ROR affiliations"

    @classmethod
    def build_task_arguments(cls, job_obj, since=None, custom_args=None, **kwargs):
        if custom_args:
            return custom_args

        if since is None and job_obj.last_runs["success"]:
            since = job_obj.last_runs["success"].started_at
        else:
            since = datetime.datetime.now()

        return {"config": {
            "readers": [
                {
                    "args": {"since": since},
                    "type": "ror-http",
                },
                {"args": {"regex": "_schema_v2\\.json$"}, "type": "zip"},
                {"type": "json"},
            ],
            "writers": [
                {
                    "args": {
                        "writer": {
                            "type": "affiliations-service",
                            "args": {"update": True},
                        }
                    },
                    "type": "async",
                }
            ],
            "transformers": [{"type": "ror-affiliations"}],
        }}
