# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary service."""

from invenio_cache import current_cache
from invenio_db import db
from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services import (
    Link,
    LinksTemplate,
    RecordService,
    RecordServiceConfig,
    SearchOptions,
    pagination_links,
)
from invenio_records_resources.services.records.components import DataComponent
from invenio_records_resources.services.records.params import (
    FilterParam,
    SuggestQueryParser,
)
from invenio_records_resources.services.records.schema import ServiceSchemaWrapper
from invenio_records_resources.services.uow import unit_of_work
from invenio_search.engine import dsl

from ..records.api import Vocabulary
from ..records.models import VocabularyType
from .components import PIDComponent, VocabularyTypeComponent
from .permissions import PermissionPolicy
from .schema import TaskSchema, VocabularySchema
from .tasks import process_datastream


def is_custom_vocabulary_type(vocabulary_type, context):
    """Check if the vocabulary type is a custom vocabulary type."""
    return vocabulary_type["id"] in current_app.config.get(
        "VOCABULARIES_CUSTOM_VOCABULARY_TYPES", []
    )


# class VocabularyMetadataList(ServiceListResult):
#     """Ensures that vocabulary metadata is returned in the proper format."""

#     def __init__(
#         self,
#         service,
#         identity,
#         results,
#         links_tpl=None,
#         links_item_tpl=None,
#     ):
#         """Constructor.

#         :params service: a service instance
#         :params identity: an identity that performed the service request
#         :params results: the search results
#         """
#         self._identity = identity
#         self._results = results
#         self._service = service
#         self._links_tpl = links_tpl
#         self._links_item_tpl = links_item_tpl

#     def to_dict(self):
#         """Formats result to a dict of hits."""
#         hits = list(self._results)

#         for hit in hits:
#             if self._links_item_tpl:
#                 hit["links"] = self._links_item_tpl.expand(self._identity, hit)

#         res = {
#             "hits": {
#                 "hits": hits,
#                 "total": len(hits),
#             }
#         }

#         if self._links_tpl:
#             res["links"] = self._links_tpl.expand(self._identity, None)

#         return res


# class VocabularyTypeService(Service):
#     """Vocabulary type service."""

#     @property
#     def schema(self):
#         """Returns the data schema instance."""
#         return ServiceSchemaWrapper(self, schema=self.config.schema)

#     @property
#     def links_item_tpl(self):
#         """Item links template."""
#         return LinksTemplate(
#             self.config.vocabularies_listing_item,
#         )

#     @property
#     def custom_vocabulary_names(self):
#         """Checks whether vocabulary is a custom vocabulary."""
#         return current_app.config.get("VOCABULARIES_CUSTOM_VOCABULARY_TYPES", [])

#     def search(self, identity):
#         """Search for vocabulary types entries."""
#         self.require_permission(identity, "list_vocabularies")

#         vocabulary_types = VocabularyType.query.all()

#         config_vocab_types = current_app.config.get(
#             "INVENIO_VOCABULARY_TYPE_METADATA", {}
#         )

#         count_terms_agg = {}
#         generic_stats = self._generic_vocabulary_statistics()
#         custom_stats = self._custom_vocabulary_statistics()

#         for k in generic_stats.keys() | custom_stats.keys():
#             count_terms_agg[k] = generic_stats.get(k, 0) + custom_stats.get(k, 0)

#         # Extend database data with configuration & aggregation data.
#         results = []
#         for db_vocab_type in vocabulary_types:
#             result = {
#                 "id": db_vocab_type.id,
#                 "pid_type": db_vocab_type.pid_type,
#                 "count": count_terms_agg.get(db_vocab_type.id, 0),
#                 "is_custom_vocabulary": db_vocab_type.id
#                 in self.custom_vocabulary_names,
#             }

#             if db_vocab_type.id in config_vocab_types:
#                 for k, v in config_vocab_types[db_vocab_type.id].items():
#                     result[k] = v

#             results.append(result)

#         return self.config.vocabularies_listing_resultlist_cls(
#             self,
#             identity,
#             results,
#             links_tpl=LinksTemplate({"self": Link("{+api}/vocabularies")}),
#             links_item_tpl=self.links_item_tpl,
#         )

#     def _custom_vocabulary_statistics(self):
#         # query database for count of terms in custom vocabularies
#         returndict = {}
#         for vocab_type in self.custom_vocabulary_names:
#             custom_service = current_service_registry.get(vocab_type)
#             record_cls = custom_service.config.record_cls
#             returndict[vocab_type] = record_cls.model_cls.query.count()

#         return returndict

#     def _generic_vocabulary_statistics(self):
#         # Opensearch query for generic vocabularies
#         config: RecordServiceConfig = current_service.config
#         search_opts = config.search

#         search = search_opts.search_cls(
#             using=current_search_client,
#             index=config.record_cls.index.search_alias,
#         )

#         search.aggs.bucket("vocabularies", {"terms": {"field": "type.id", "size": 100}})

#         search_result = search.execute()
#         buckets = search_result.aggs.to_dict()["vocabularies"]["buckets"]

#         return {bucket["key"]: bucket["doc_count"] for bucket in buckets}


class VocabularySearchOptions(SearchOptions):
    """Search options."""

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


class VocabulariesService(RecordService):
    """Vocabulary service."""

    @property
    def task_schema(self):
        """Returns the data schema instance."""
        return ServiceSchemaWrapper(self, schema=self.config.task_schema)

    @unit_of_work()
    def create_type(self, identity, id, pid_type, uow=None):
        """Create a new vocabulary type."""
        self.require_permission(identity, "manage")
        type_ = VocabularyType.create(id=id, pid_type=pid_type)
        return type_

    def search(
        self, identity, params=None, search_preference=None, type=None, **kwargs
    ):
        """Search for vocabulary entries."""
        self.require_permission(identity, "search")

        # If not found, NoResultFound is raised (caught by the resource).
        vocabulary_type = VocabularyType.query.filter_by(id=type).one()

        # Prepare and execute the search
        params = params or {}
        search_result = self._search(
            "search",
            identity,
            params,
            search_preference,
            extra_filter=dsl.Q("term", type__id=vocabulary_type.id),
            **kwargs
        ).execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_search,
                context={
                    "args": params,
                    "type": vocabulary_type.id,
                },
            ),
            links_item_tpl=self.links_item_tpl,
        )

    def read_all(self, identity, fields, type, cache=True, extra_filter="", **kwargs):
        """Search for records matching the querystring."""
        cache_key = type + "_" + str(extra_filter) + "_" + "-".join(fields)
        results = current_cache.get(cache_key)
        search_query = dsl.Q("match_all")

        if not results:
            # If not found, NoResultFound is raised (caught by the resource).
            vocabulary_type = VocabularyType.query.filter_by(id=type).one()
            vocab_id_filter = dsl.Q("term", type__id=vocabulary_type.id)
            if extra_filter:
                vocab_id_filter = vocab_id_filter & extra_filter
            results = self._read_many(
                identity, search_query, fields, extra_filter=vocab_id_filter, **kwargs
            )
            if cache:
                # ES DSL Response is not pickable.
                # If saved in cache serialization wont work with to_dict()
                current_cache.set(cache_key, results.to_dict())

        else:
            search = self.create_search(
                identity=identity,
                record_cls=self.record_cls,
                search_opts=self.config.search,
                permission_action="search",
            ).query(search_query)

            results = dsl.response.Response(search, results)

        return self.result_list(self, identity, results)

    def read_many(self, identity, type, ids, fields=None, **kwargs):
        """Search for records matching the querystring filtered by ids."""
        search_query = dsl.Q("match_all")
        vocabulary_type = VocabularyType.query.filter_by(id=type).one()
        vocab_id_filter = dsl.Q("term", type__id=vocabulary_type.id)
        filters = []

        for id_ in ids:
            filters.append(dsl.Q("term", **{"id": id_}))
        filter = dsl.Q("bool", minimum_should_match=1, should=filters)
        filter = filter & vocab_id_filter
        results = self._read_many(
            identity, search_query, fields, extra_filter=filter, **kwargs
        )

        return self.result_list(self, identity, results)

    def launch(self, identity, data):
        """Create a task.

        FIXME: This is a PoC. The final implementation should resemble
        the PIDs, having a sub-service and a manager. If persistance is
        added UoW should be used.
        """
        self.require_permission(identity, "manage")
        task_config, _ = self.task_schema.load(
            data,
            context={"identity": identity},  # FIXME: is this needed
            raise_errors=True,
        )
        process_datastream.delay(task_config)

        # 202 if accepted, otherwise it will be caught by an error handler
        return True
