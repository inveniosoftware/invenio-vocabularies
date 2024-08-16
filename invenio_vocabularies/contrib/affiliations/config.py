# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary affiliations configuration."""

from flask import current_app
from invenio_i18n import get_locale
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services import SearchOptions
from invenio_records_resources.services.records.components import DataComponent
from invenio_records_resources.services.records.params import SuggestQueryParser
from werkzeug.local import LocalProxy

from ...services.components import PIDComponent

affiliation_schemes = LocalProxy(
    lambda: current_app.config["VOCABULARIES_AFFILIATION_SCHEMES"]
)
localized_title = LocalProxy(lambda: f"title.{get_locale()}^20")


class AffiliationsSearchOptions(SearchOptions):
    """Search options."""

    suggest_parser_cls = SuggestQueryParser.factory(
        fields=[
            "name^100",
            "acronym.keyword^100",
            "acronym^40",
            localized_title,
            "id^20",
            "aliases^20",
        ],
        type="most_fields",  # https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html#multi-match-types
        fuzziness="AUTO",  # https://www.elastic.co/guide/en/elasticsearch/reference/current/common-options.html#fuzziness
    )

    sort_default = "bestmatch"

    sort_default_no_query = "name"

    sort_options = {
        "bestmatch": dict(
            title=_("Best match"),
            fields=["_score"],  # ES defaults to desc on `_score` field
        ),
        "name": dict(
            title=_("Name"),
            fields=["name_sort"],
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
