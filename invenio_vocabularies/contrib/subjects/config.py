# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Subjects configuration."""

from flask import current_app
from invenio_i18n import get_locale
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services import SearchOptions
from invenio_records_resources.services.records.components import DataComponent
from werkzeug.local import LocalProxy

from ...services.components import PIDComponent
from ...services.querystr import FilteredSuggestQueryParser

subject_schemes = LocalProxy(
    lambda: current_app.config["VOCABULARIES_SUBJECTS_SCHEMES"]
)
localized_title = LocalProxy(lambda: f"title.{get_locale()}^20")


gemet_file_url = LocalProxy(
    lambda: current_app.config["VOCABULARIES_SUBJECTS_GEMET_FILE_URL"]
)

euroscivoc_file_url = LocalProxy(
    lambda: current_app.config["VOCABULARIES_SUBJECTS_EUROSCIVOC_FILE_URL"]
)


class SubjectsSearchOptions(SearchOptions):
    """Search options."""

    suggest_parser_cls = FilteredSuggestQueryParser.factory(
        filter_field="scheme",
        fields=[  # suggest fields
            "subject^100",
            localized_title,
            "synonyms^20",
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
