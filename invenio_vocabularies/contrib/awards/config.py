# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary awards configuration."""

from flask import current_app
from flask_babelex import lazy_gettext as _
from invenio_records_resources.services import SearchOptions
from invenio_records_resources.services.records.components import DataComponent
from invenio_records_resources.services.records.params import \
    SuggestQueryParser
from werkzeug.local import LocalProxy

from ...services.components import ModelPIDComponent

award_schemes = LocalProxy(
    lambda: current_app.config["VOCABULARIES_AWARD_SCHEMES"]
)


class AwardsSearchOptions(SearchOptions):
    """Search options."""

    suggest_parser_cls = SuggestQueryParser.factory(
        fields=[
            'acronym^100',
            'title.*^50',
            'title.*._2gram',
            'title.*._3gram',
            'number^10'
        ],
    )


service_components = [
    # Order of components are important!
    DataComponent,
    ModelPIDComponent,
]
