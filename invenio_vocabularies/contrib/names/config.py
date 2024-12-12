# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary names configuration."""

from flask import current_app
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services import SearchOptions
from invenio_records_resources.services.records.components import (
    DataComponent,
    RelationsComponent,
)
from invenio_records_resources.services.records.queryparser import (
    CompositeSuggestQueryParser,
)
from werkzeug.local import LocalProxy

from ...services.components import PIDComponent
from .components import InternalIDComponent

names_schemes = LocalProxy(lambda: current_app.config["VOCABULARIES_NAMES_SCHEMES"])


class NamesSearchOptions(SearchOptions):
    """Search options."""

    suggest_parser_cls = CompositeSuggestQueryParser.factory(
        fields=[
            "name^5",
            # We boost the affiliation acronym fields, since they're short and more
            # likely to be used in a query.
            "affiliations.acronym.keyword^3",
            "affiliations.acronym",
            "affiliations.name",
            # Allow to search identifiers directly (e.g. ORCID)
            "identifiers.identifier",
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
    InternalIDComponent,
    DataComponent,
    PIDComponent,
    RelationsComponent,
]
