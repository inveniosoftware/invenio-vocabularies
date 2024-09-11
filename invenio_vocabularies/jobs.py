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
from invenio_i18n import gettext as _


class ArgsSchema(Schema):

    since = TZDateTime(
        timezone=timezone.utc,
        format="iso",
        metadata={
            "description":
                _("YYYY-MM-DD HH:mm format. Leave field empty if it should continue since last successful run")
        },
    )
    job_arg_schema = fields.String(
        metadata={"type": "hidden"},
        dump_default="ArgsSchema",
        load_default="ArgsSchema",
    )


class ProcessDataStreamJob(JobType):

    arguments_schema = ArgsSchema
    task = process_datastream
    id = None


class ProcessRORAffiliationsJob(ProcessDataStreamJob):
    """Process ROR affiliations datastream registered task."""

    description = "Process ROR affiliations"
    title = "Load ROR affiliations"
    id = "process_ror_affiliations"

    @classmethod
    def default_args(cls, job_obj, since=None, **kwargs):
        if since is None and job_obj.last_runs["success"]:
            since = job_obj.last_runs["success"].started_at
        else:
            since = datetime.datetime.now()

        return {
            "config": {
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
            }
        }
