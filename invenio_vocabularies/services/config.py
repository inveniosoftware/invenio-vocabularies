# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary services configs."""

import sqlalchemy as sa
from flask import current_app
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services import (
    RecordEndpointLink,
    RecordServiceConfig,
    SearchOptions,
    pagination_endpoint_links,
)
from invenio_records_resources.services.records.components import DataComponent
from invenio_records_resources.services.records.params import (
    FilterParam,
    SuggestQueryParser,
)

from ..records.api import Vocabulary
from ..records.models import VocabularyType
from . import results
from .components import PIDComponent, VocabularyTypeComponent
from .permissions import PermissionPolicy
from .schema import TaskSchema, VocabularySchema


def is_custom_vocabulary_type(vocabulary_type, context):
    """Check if the vocabulary type is a custom vocabulary type."""
    return vocabulary_type["id"] in current_app.config.get(
        "VOCABULARIES_CUSTOM_VOCABULARY_TYPES", []
    )


class VocabularySearchOptions(SearchOptions):
    """Search options for vocabularies."""

    params_interpreters_cls = [
        FilterParam.factory(param="tags", field="tags"),
    ] + SearchOptions.params_interpreters_cls

    suggest_parser_cls = SuggestQueryParser.factory(
        fields=[
            "id.text^100",
            "id.text._2gram",
            "id.text._3gram",
            "title.en^5",
            "title.en._2gram",
            "title.en._3gram",
        ],
    )

    sort_default = "bestmatch"

    sort_default_no_query = "title"

    sort_options = {
        "bestmatch": dict(
            title=_("Best match"),
            fields=["_score"],  # ES defaults to desc on `_score` field
        ),
        "title": dict(
            title=_("Title"),
            fields=["title_sort"],
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


class VocabularyTypeSearchOptions(SearchOptions):
    """Search options for vocabulary types."""

    sort_options = {
        "id": dict(
            title=_("ID"),
            fields=["id"],
        ),
    }

    sort_default = "id"

    sort_default_no_query = "id"

    sort_direction_options = {
        "asc": dict(title=_("Ascending"), fn=sa.asc),
        "desc": dict(title=_("Descending"), fn=sa.desc),
    }

    sort_direction_default = "asc"


class VocabulariesServiceConfig(RecordServiceConfig):
    """Vocabulary service configuration."""

    service_id = "vocabularies"
    indexer_queue_name = "vocabularies"
    permission_policy_cls = PermissionPolicy
    record_cls = Vocabulary
    schema = VocabularySchema
    task_schema = TaskSchema

    search = VocabularySearchOptions

    components = [
        # Order of components are important!
        VocabularyTypeComponent,
        DataComponent,
        PIDComponent,
    ]

    links_item = {
        "self": RecordEndpointLink(
            "vocabularies.read",
            params=["type", "pid_value"],
            # RecordEndpointLink takes care of the pid_value
            vars=lambda record, vars: vars.update(type=record.type.id),
        ),
    }

    links_search = pagination_endpoint_links(
        "vocabularies.search",
        params=["type"],
    )


class VocabularyTypesServiceConfig(RecordServiceConfig):
    """Vocabulary types service configuration."""

    service_id = "vocabulary_types"
    permission_policy_cls = PermissionPolicy
    record_cls = VocabularyType
    schema = VocabularySchema  # Works but should be VocabularyTypeSchema if this is defined at some point
    result_list_cls = results.VocabularyTypeList

    # An individual vocabulary type endpoint doesn't exist
    links_item = {}

    search = VocabularyTypeSearchOptions

    components = [
        # Order of components are important!
        VocabularyTypeComponent,
        DataComponent,
        PIDComponent,
    ]

    links_search = pagination_endpoint_links("vocabulary_types.search")
