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
from invenio_records_resources.services.records.queryparser import (
    CompositeSuggestQueryParser,
)
from werkzeug.local import LocalProxy

from ...services.components import PIDComponent

affiliation_schemes = LocalProxy(
    lambda: current_app.config["VOCABULARIES_AFFILIATION_SCHEMES"]
)
affiliation_edmo_country_mappings = LocalProxy(
    lambda: current_app.config["VOCABULARIES_AFFILIATIONS_EDMO_COUNTRY_MAPPING"]
)
localized_title = LocalProxy(lambda: f"title.{get_locale()}^2")


class AffiliationsSearchOptions(SearchOptions):
    """Search options."""

    suggest_parser_cls = CompositeSuggestQueryParser.factory(
        fields=[
            # We boost the acronym fields, since they're smaller words and are more
            # likely to be used in a query.
            "acronym.keyword^50",
            "acronym^10",
            "name^10",
            # Aliases can sometimes be shorter, so we boost them a bit.
            "aliases^5",
            localized_title,
            # Allow to search identifiers directly (e.g. ROR)
            "identifiers.identifier",
            "country_name",
        ],
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
