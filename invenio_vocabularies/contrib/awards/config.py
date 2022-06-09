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
from invenio_records_resources.services.records.components import (
    DataComponent,
    RelationsComponent,
)
from invenio_records_resources.services.records.facets import TermsFacet
from invenio_records_resources.services.records.params import SuggestQueryParser
from werkzeug.local import LocalProxy

from ...services.components import ModelPIDComponent
from ..funders.facets import FundersLabels

award_schemes = LocalProxy(lambda: current_app.config["VOCABULARIES_AWARD_SCHEMES"])

awards_openaire_funders_mapping = LocalProxy(
    lambda: current_app.config["VOCABULARIES_AWARDS_OPENAIRE_FUNDERS"]
)

awards_ec_ror_id = LocalProxy(
    lambda: current_app.config["VOCABULARIES_AWARDS_EC_ROR_ID"]
)


class AwardsSearchOptions(SearchOptions):
    """Search options."""

    suggest_parser_cls = SuggestQueryParser.factory(
        fields=[
            "acronym^100",
            "title.*^50",
            "title.*._2gram",
            "title.*._3gram",
            "number^10",
        ],
    )

    facets = {
        "funders": TermsFacet(
            field="funder.id", label=_("Funders"), value_labels=FundersLabels("funders")
        )
    }


service_components = [
    # Order of components are important!
    DataComponent,
    ModelPIDComponent,
    RelationsComponent,
]
