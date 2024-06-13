# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary services configs."""

from flask import current_app
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services import (
    Link,
    LinksTemplate,
    RecordService,
    RecordServiceConfig,
    SearchOptions,
    pagination_links,
)
from invenio_records_resources.services.base import (
    ConditionalLink,
    Service,
    ServiceListResult,
)
from invenio_records_resources.services.records.components import DataComponent
from invenio_records_resources.services.records.params import (
    FilterParam,
    SuggestQueryParser,
)
from sqlalchemy import asc, desc

from ..records.api import Vocabulary
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

    # TODO: Is this still necessary here?
    params_interpreters_cls = [
        FilterParam.factory(param="tags", field="tags"),
    ] + SearchOptions.params_interpreters_cls

    # TODO: Is this still necessary here?
    suggest_parser_cls = SuggestQueryParser.factory(
        fields=[
            "id.text^100",
            "id.text._2gram",
            "id.text._3gram",
        ],
    )

    sort_options = {
        "id": dict(
            title=_("ID"),
            fields=["id"],
        ),
    }

    sort_default = "id"

    sort_default_no_query = "id"

    # TODO: Check if these options are actually necessary
    sort_direction_options = {
        "asc": dict(title=_("Ascending"), fn=asc),
        "desc": dict(title=_("Descending"), fn=desc),
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
        "self": Link(
            "{+api}/vocabularies/{type}/{id}",
            vars=lambda record, vars: vars.update(
                {
                    "id": record.pid.pid_value,
                    "type": record.type.id,
                }
            ),
        ),
    }

    links_search = pagination_links("{+api}/vocabularies/{type}{?args*}")


class VocabularyTypesServiceConfig(RecordServiceConfig):
    """Vocabulary types service configuration."""

    service_id = "vocabulary_types"
    permission_policy_cls = PermissionPolicy
    record_cls = Vocabulary  # TODO: Is this correct?
    schema = VocabularySchema
    task_schema = TaskSchema
    vocabularies_listing_resultlist_cls = results.VocabularyMetadataList

    vocabularies_listing_item = {
        "self": ConditionalLink(
            cond=is_custom_vocabulary_type,
            if_=Link(
                "{+api}/{id}",
                vars=lambda vocab_type, vars: vars.update({"id": vocab_type["id"]}),
            ),
            else_=Link(
                "{+api}/vocabularies/{id}",
                vars=lambda vocab_type, vars: vars.update({"id": vocab_type["id"]}),
            ),
        )
    }

    search = VocabularyTypeSearchOptions

    components = [
        # Order of components are important!
        VocabularyTypeComponent,
        DataComponent,
        PIDComponent,
    ]

    links_item = {
        "self": Link(
            "{+api}/vocabularies/{type}/{id}",
            vars=lambda record, vars: vars.update(
                {
                    "id": record.pid.pid_value,
                    "type": record.type.id,
                }
            ),
        ),
    }

    links_search = pagination_links("{+api}/vocabularies/{type}{?args*}")
