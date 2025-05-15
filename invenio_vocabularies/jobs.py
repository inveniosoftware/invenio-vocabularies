# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Jobs module."""

import datetime

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
        return {"config": {**ORCID_PRESET_DATASTREAM_CONFIG}}
