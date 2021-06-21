# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary affiliations configuration."""

from flask_babelex import lazy_gettext as _
from invenio_records_resources.services import SearchOptions
from invenio_records_resources.services.records.components import DataComponent
from invenio_records_resources.services.records.params import \
    SuggestQueryParser

from ...services.components import PIDComponent


class AffiliationsSearchOptions(SearchOptions):
    """Search options."""

    suggest_parser_cls = SuggestQueryParser.factory(
        fields=[  # TODO: Tweak with name and acronym
            'id.text^100',
            'id.text._2gram',
            'id.text._3gram',
            'title.en^5',
            'title.en._2gram',
            'title.en._3gram',
        ],
    )

    sort_default = 'bestmatch'

    sort_default_no_query = 'name'

    sort_options = {
        "bestmatch": dict(
            title=_('Best match'),
            fields=['_score'],  # ES defaults to desc on `_score` field
        ),
        "title": dict(
            title=_('Title'),
            fields=['title_sort'],
        ),
        "newest": dict(
            title=_('Newest'),
            fields=['-created'],
        ),
        "oldest": dict(
            title=_('Oldest'),
            fields=['created'],
        ),
    }


service_components = [
    # Order of components are important!
    DataComponent,
    PIDComponent,
]
