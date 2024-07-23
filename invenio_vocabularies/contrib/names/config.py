# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
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
from invenio_records_resources.services.records.params import SuggestQueryParser
from werkzeug.local import LocalProxy

from ...services.components import PIDComponent

names_schemes = LocalProxy(lambda: current_app.config["VOCABULARIES_NAMES_SCHEMES"])


class NamesSearchOptions(SearchOptions):
    """Search options."""

    suggest_parser_cls = SuggestQueryParser.factory(
        fields=[
            "name.suggest^80",
            "name^80",
            "family_name^70",
            "given_name.suggest^100",
            "given_name^100",
            "identifiers.identifier^20",
            "affiliations.name^10",
        ],  # type has to be bool_prefix to use suggest._index_prefix field during querying
        operator="AND",
        fuzziness="AUTO",
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
    RelationsComponent,
]
