# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Jobs module."""

from datetime import datetime, timedelta

from flask import current_app
from invenio_i18n import lazy_gettext as _
from invenio_jobs.jobs import JobType

from invenio_vocabularies.services.tasks import process_datastream

from .contrib.names.datastreams import ORCID_PRESET_DATASTREAM_CONFIG


class ProcessDataStreamJob(JobType):
    """Generic process data stream job type."""

    task = process_datastream


class ProcessRORAffiliationsJob(ProcessDataStreamJob):
    """Process ROR affiliations datastream registered task."""

    description = _("Process ROR affiliations")
    title = _("Load ROR affiliations")
    id = "process_ror_affiliations"

    @classmethod
    def build_task_arguments(cls, job_obj, since=None, **kwargs):
        """Process ROR affiliations."""
        # NOTE: Update is set to False for now given we don't have the logic to re-index dependent records yet.
        # Since jobs support custom args, update true can be passed via that.
        return {
            "config": {
                "readers": [
                    {
                        "args": {"since": since},
                        "type": "ror-http",
                    },
                    {"args": {"regex": "-ror-data\\.json$"}, "type": "zip"},
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

    description = _("Process ROR funders")
    title = _("Load ROR funders")
    id = "process_ror_funders"

    @classmethod
    def build_task_arguments(cls, job_obj, since=None, **kwargs):
        """Process ROR funders."""
        # NOTE: Update is set to False for now given we don't have the logic to re-index dependent records yet.
        # Since jobs support custom args, update true can be passed via that.
        return {
            "config": {
                "readers": [
                    {
                        "args": {"since": since},
                        "type": "ror-http",
                    },
                    {"args": {"regex": "-ror-data\\.json$"}, "type": "zip"},
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

    description = _("Import awards from OpenAIRE")
    title = _("Import Awards OpenAIRE")
    id = "import_awards_openaire"

    @classmethod
    def build_task_arguments(cls, job_obj, since=None, **kwargs):
        """Process awards OpenAIRE."""
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

    description = _("Update awards from CORDIS")
    title = _("Update Awards CORDIS")
    id = "update_awards_cordis"

    @classmethod
    def build_task_arguments(cls, job_obj, since=None, **kwargs):
        """Process awards Cordis."""
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

    description = _("Import ORCID data")
    title = _("Import ORCID data")
    id = "import_orcid"

    @classmethod
    def build_task_arguments(cls, job_obj, since=None, **kwargs):
        """Process ORCID data."""
        task_args = {"config": {**ORCID_PRESET_DATASTREAM_CONFIG}}
        for reader in task_args["config"]["readers"]:
            # Assign since to all readers of the ORCID job
            # It is the responsibility of the reader to handle it or ignore it
            reader["args"] = {**reader.get("args", {}), "since": str(since)}
        return task_args

    @classmethod
    def _build_task_arguments(cls, job_obj, since=None, custom_args=None, **kwargs):
        """Build dict of arguments injected on task execution.

        :param job_obj (Job): the Job object.
        :param since (datetime): last time the job was executed.
        :param custom_args (dict): when provided, takes precedence over any other
            provided argument.
        :return: a dict of arguments to be injected on task execution.
        """
        if custom_args:
            return custom_args

        if since is None:
            """We set since to a time in the past defined by the VOCABULARIES_ORCID_SYNC_SINCE."""

            since = datetime.now() - timedelta(
                **current_app.config["VOCABULARIES_ORCID_SYNC_SINCE"]
            )
        """
        Otherwise, since is already specified as a datetime with a timezone (see PredefinedArgsSchema) or we have never
        run the job before so there is no logical value.
        """
        return {**cls.build_task_arguments(job_obj, since=since, **kwargs)}
