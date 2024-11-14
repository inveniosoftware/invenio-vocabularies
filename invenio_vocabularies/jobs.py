# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Jobs module."""

import datetime
from datetime import timezone

from invenio_i18n import gettext as _
from invenio_jobs.jobs import JobType
from marshmallow import Schema, fields
from marshmallow_utils.fields import TZDateTime

from invenio_vocabularies.services.tasks import process_datastream

from .contrib.names.datastreams import ORCID_PRESET_DATASTREAM_CONFIG


class ArgsSchema(Schema):
    """Schema of task input arguments."""

    since = TZDateTime(
        timezone=timezone.utc,
        format="iso",
        metadata={
            "description": _(
                "YYYY-MM-DD HH:mm format. "
                "Leave field empty if it should continue since last successful run."
            )
        },
    )
    job_arg_schema = fields.String(
        metadata={"type": "hidden"},
        dump_default="ArgsSchema",
        load_default="ArgsSchema",
    )


class ProcessDataStreamJob(JobType):
    """Generic process data stream job type."""

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
        """Generate default job arguments here."""
        if since is None and job_obj.last_runs["success"]:
            since = job_obj.last_runs["success"].started_at
        else:
            since = since or datetime.datetime.now()

        # NOTE: Update is set to False for now given we don't have the logic to re-index dependent records yet.
        # Since jobs support custom args, update true can be passed via that.
        return {
            "config": {
                "readers": [
                    {
                        "args": {"since": str(since)},
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
                                "args": {"update": False},
                            }
                        },
                        "type": "async",
                    }
                ],
                "transformers": [{"type": "ror-affiliations"}],
            }
        }


class ProcessRORFundersJob(ProcessDataStreamJob):
    """Process ROR funders datastream registered task."""

    description = "Process ROR funders"
    title = "Load ROR funders"
    id = "process_ror_funders"

    @classmethod
    def default_args(cls, job_obj, since=None, **kwargs):
        """Generate default job arguments here."""
        if since is None and job_obj.last_runs["success"]:
            since = job_obj.last_runs["success"].started_at
        else:
            since = since or datetime.datetime.now()

        # NOTE: Update is set to False for now given we don't have the logic to re-index dependent records yet.
        # Since jobs support custom args, update true can be passed via that.
        return {
            "config": {
                "readers": [
                    {
                        "args": {"since": str(since)},
                        "type": "ror-http",
                    },
                    {"args": {"regex": "_schema_v2\\.json$"}, "type": "zip"},
                    {"type": "json"},
                ],
                "writers": [
                    {
                        "args": {
                            "writer": {
                                "type": "funders-service",
                                "args": {"update": False},
                            }
                        },
                        "type": "async",
                    }
                ],
                "transformers": [{"type": "ror-funders"}],
            }
        }


class ImportAwardsOpenAIREJob(ProcessDataStreamJob):
    """Import awards from OpenAIRE registered task."""

    description = "Import awards from OpenAIRE"
    title = "Import Awards OpenAIRE"
    id = "import_awards_openaire"

    @classmethod
    def default_args(cls, job_obj, **kwargs):
        """Generate default job arguments."""
        return {
            "config": {
                "readers": [
                    {
                        "type": "openaire-http",
                        "args": {"origin": "diff", "tar_href": "/project.tar"},
                    },
                    {
                        "type": "tar",
                        "args": {
                            "mode": "r",
                            "regex": "\\.json.gz$",
                        },
                    },
                    {"type": "gzip"},
                    {"type": "jsonl"},
                ],
                "transformers": [{"type": "openaire-award"}],
                "writers": [
                    {"args": {"writer": {"type": "awards-service"}}, "type": "async"}
                ],
            }
        }


class UpdateAwardsCordisJob(ProcessDataStreamJob):
    """Update awards from CORDIS registered task."""

    description = "Update awards from CORDIS"
    title = "Update Awards CORDIS"
    id = "update_awards_cordis"

    @classmethod
    def default_args(cls, job_obj, **kwargs):
        """Generate default job arguments."""
        return {
            "config": {
                "readers": [
                    {"args": {"origin": "HE"}, "type": "cordis-project-http"},
                    {"args": {"mode": "r", "regex": "\\.xml$"}, "type": "zip"},
                    {"args": {"root_element": "project"}, "type": "xml"},
                ],
                "transformers": [{"type": "cordis-award"}],
                "writers": [
                    {
                        "args": {"writer": {"type": "cordis-awards-service"}},
                        "type": "async",
                    }
                ],
            }
        }


class ImportORCIDJob(ProcessDataStreamJob):
    """Import ORCID data registered task."""

    description = "Import ORCID data"
    title = "Import ORCID data"
    id = "import_orcid"

    @classmethod
    def default_args(cls, job_obj, **kwargs):
        """Generate default job arguments."""
        return {"config": {**ORCID_PRESET_DATASTREAM_CONFIG}}
