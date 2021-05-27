# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary service."""

from elasticsearch_dsl.query import Q
from elasticsearch_dsl.response import Response
from flask_babelex import lazy_gettext as _
from invenio_cache import current_cache
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

    def read_all(self, identity, fields, type, cache=True, **kwargs):
        """Search for records matching the querystring."""
        cache_key = "-".join(fields)
        results = current_cache.get(cache_key)
        es_query = Q("match_all")

        if not results:
            # If not found, NoResultFound is raised (caught by the resource).
            vocabulary_type = VocabularyType.query.filter_by(id=type).one()
            vocab_id_filter = Q('term', type__id=vocabulary_type.id)

            results = self._read_many(
                identity, es_query, fields,
                extra_filter=vocab_id_filter, **kwargs)
            if cache:
                # ES DSL Response is not pickable.
                # If saved in cache serialization wont work with to_dict()
                current_cache.set(cache_key, results.to_dict())

        else:
            search = self.create_search(
                identity=identity,
                record_cls=self.record_cls,
                search_opts=self.config.search,
                permission_action='search',
            ).query(es_query)

            results = Response(search, results)

        return self.result_list(self, identity, results)
