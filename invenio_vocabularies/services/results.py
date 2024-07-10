# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 Uni Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary results."""

from flask import current_app
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services import RecordServiceConfig
from invenio_records_resources.services.records.results import RecordList
from invenio_search import current_search_client

from ..proxies import current_service


class VocabularyTypeList(RecordList):
    """Ensures that vocabulary type metadata is returned in the proper format."""

    @property
    def total(self):
        """Get total number of hits."""
        return self._results.total

    @property
    def custom_vocabulary_names(self):
        """Checks whether vocabulary is a custom vocabulary."""
        return current_app.config.get("VOCABULARIES_CUSTOM_VOCABULARY_TYPES", [])

    def to_dict(self):
        """Formats result to a dict of hits."""
        config_vocab_types = current_app.config.get(
            "INVENIO_VOCABULARY_TYPE_METADATA", {}
        )

        count_terms_agg = {}
        generic_stats = self._generic_vocabulary_statistics()
        custom_stats = self._custom_vocabulary_statistics()

        for k in generic_stats.keys() | custom_stats.keys():
            count_terms_agg[k] = generic_stats.get(k, 0) + custom_stats.get(k, 0)

        hits = self._results.items

        # Extend database data with configuration & aggregation data.
        results = []
        for db_vocab_type in hits:
            result = {
                "id": db_vocab_type.id,
                "pid_type": db_vocab_type.pid_type,
                "count": count_terms_agg.get(db_vocab_type.id, 0),
                "is_custom_vocabulary": db_vocab_type.id
                in self.custom_vocabulary_names,
            }

            if db_vocab_type.id in config_vocab_types:
                for k, v in config_vocab_types[db_vocab_type.id].items():
                    result[k] = v

            results.append(result)

        for hit in results:
            if self._links_item_tpl:
                hit["links"] = self._links_item_tpl.expand(self._identity, hit)

        res = {
            "hits": {
                "hits": results,
                "total": self.total,
            }
        }

        if self._params:
            if self._links_tpl:
                res["links"] = self._links_tpl.expand(self._identity, self.pagination)

        return res

    def _custom_vocabulary_statistics(self):
        # query database for count of terms in custom vocabularies
        returndict = {}
        for vocab_type in self.custom_vocabulary_names:
            custom_service = current_service_registry.get(vocab_type)
            record_cls = custom_service.config.record_cls
            returndict[vocab_type] = record_cls.model_cls.query.count()

        return returndict

    def _generic_vocabulary_statistics(self):
        # Opensearch query for generic vocabularies
        config: RecordServiceConfig = (
            current_service.config
        )  # TODO: Where to get the config from here? current_service is None
        search_opts = config.search

        search = search_opts.search_cls(
            using=current_search_client,
            index=config.record_cls.index.search_alias,
        )

        search.aggs.bucket("vocabularies", {"terms": {"field": "type.id", "size": 100}})

        search_result = search.execute()
        buckets = search_result.aggs.to_dict()["vocabularies"]["buckets"]

        return {bucket["key"]: bucket["doc_count"] for bucket in buckets}
