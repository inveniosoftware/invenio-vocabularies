# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Subjects configuration."""

from flask_babelex import lazy_gettext as _
from invenio_records_resources.services import SearchOptions
from invenio_records_resources.services.records.components import DataComponent

from ...services.components import PIDComponent
from ...services.querystr import FilteredSuggestQueryParser


class SubjectsSearchOptions(SearchOptions):
    """Search options."""

    suggest_parser_cls = FilteredSuggestQueryParser.factory(
        filter_field="scheme",
        fields=[  # suggest fields
            "subject^100",
            "subject._2gram",
            "subject._3gram",
        ],
    )

    sort_default = "bestmatch"

    sort_default_no_query = "subject"

    sort_options = {
        "bestmatch": dict(
            title=_("Best match"),
            fields=["_score"],  # ES defaults to desc on `_score` field
        ),
        "subject": dict(
            title=_("Name"),
            fields=["subject_sort"],
        ),
        "newest": dict(
            title=_("Newest"),
            fields=["-created"],
        ),
        "oldest": dict(
            title=_("Oldest"),
            fields=["created"],
        ),
    }


service_components = [
    # Order of components are important!
    DataComponent,
    PIDComponent,
]
