# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary service."""

from elasticsearch_dsl.query import Q
from flask_babelex import lazy_gettext as _
from invenio_db import db
from invenio_records_resources.services import Link, LinksTemplate, \
    RecordService, RecordServiceConfig, SearchOptions, pagination_links
from invenio_records_resources.services.records.components import DataComponent
from invenio_records_resources.services.records.params import FilterParam, \
    SuggestQueryParser

from ..records.api import Vocabulary
from ..records.models import VocabularyType
from .components import PIDComponent, VocabularyTypeComponent
from .permissions import PermissionPolicy
from .schema import VocabularySchema


class VocabularySearchOptions(SearchOptions):
    """Search options."""

    params_interpreters_cls = [
        FilterParam.factory(param='tags', field='tags'),
    ] + SearchOptions.params_interpreters_cls

    suggest_parser_cls = SuggestQueryParser.factory(
        fields=[
            'id.text^100',
            'id.text._2gram',
            'id.text._3gram',
            'title.en^5',
            'title.en._2gram',
            'title.en._3gram',
        ],
    )

    sort_default = 'bestmatch'

    sort_default_no_query = 'title'

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


class VocabulariesServiceConfig(RecordServiceConfig):
    """Vocabulary service configuration."""

    permission_policy_cls = PermissionPolicy
    record_cls = Vocabulary
    schema = VocabularySchema

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
            vars=lambda record, vars: vars.update({
                "id": record.pid.pid_value,
                "type": record.type.id,
            })
        ),
    }

    links_search = pagination_links("{+api}/vocabularies/{type}{?args*}")


class VocabulariesService(RecordService):
    """Vocabulary service."""

    def create_type(self, identity, id, pid_type):
        """Create a new vocabulary type."""
        self.require_permission(identity, "manage")
        type_ = VocabularyType.create(id=id, pid_type=pid_type)
        db.session.commit()
        return type_

    def search(self, identity, params=None, es_preference=None, type=None,
               **kwargs):
        """Search for vocabulary entries."""
        self.require_permission(identity, 'search')

        # If not found, NoResultFound is raised (caught by the resource).
        vocabulary_type = VocabularyType.query.filter_by(id=type).one()

        # Prepare and execute the search
        params = params or {}
        search_result = self._search(
            'search',
            identity,
            params,
            es_preference,
            extra_filter=Q('term', type__id=vocabulary_type.id),
            **kwargs
        ).execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(self.config.links_search, context={
                "args": params,
                "type": vocabulary_type.id,
            }),
            links_item_tpl=self.links_item_tpl,
        )
