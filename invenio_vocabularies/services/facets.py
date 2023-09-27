# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary facets."""

import time
from functools import lru_cache

from flask_principal import AnonymousIdentity
from invenio_i18n.ext import current_i18n
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services.errors import FacetNotFoundError
from marshmallow_utils.fields.babel import gettext_from_dict
from speaklater import make_lazy_string
from sqlalchemy.exc import NoResultFound

from ..proxies import current_service

cached_labels = dict()
cached_labels_ttl = dict()


def get_service(service_id):
    """Get the service object by id.

    It is required to access the registry lazily, to avoid out of
    application context errors.
    """
    return (
        current_service_registry.get(service_id) if service_id else current_service
    )


def get_vocabs(service_id, type, fields, ids):
    """Fetch vocabulary values by ids, using the service."""
    service = get_service(service_id)
    vocabs = service.read_many(AnonymousIdentity(), type=type, ids=list(ids), fields=list(fields))
    return vocabs.hits


def get_ttl_hash(seconds=3600):
    """Return the same value withing `seconds` time period. Default 1 hour."""
    return round(time.time() / seconds)


# @lru_cache(maxsize=128)
# def cached_label(service_id, type, fields, id_, ttl_hash=None):
#     """Single."""
#     return cached_labels[(service_id, type, fields)].get(id_, None)

# @lru_cache(maxsize=128)
# def cached_vocabs(service_id, type, fields, ids, ttl_hash=None):
#     """Cache vocabulary values by type with a simple process in-memory cache.

#     This cache is meant to greatly optimize performance when getting the title of
#     each facet, during searches, and to avoid accessing DB/Search each time.
#     This cache suffer of a slower warm up at the first cache miss when each process is
#     restarted. A data store cache could be also used as mitigation, with the drawback
#     of the added network latency.

#     `@lru_cache` is threadsafe. `maxsize` is set to 32, assuming that there are not more
#     than 32 (multiple of 2 for optimization) different vocabularies types defined
#     in the instance.

#     The ttl_hash kwarg is necessary to make the cache expiring, by changing the hash key
#     after the defined time.
#     """
#     return get_vocabs(service_id, type=type, ids=list(ids), fields=list(fields))


def lazy_get_label(vocab_item):
    """Lazy evaluation of a localized vocabulary label."""
    params = {"locale": current_i18n.locale, "default_locale": "en"}

    return make_lazy_string(gettext_from_dict, vocab_item, **params)

from datetime import datetime, timedelta
class VocabularyLabels:
    """Fetching of vocabulary labels for facets."""

    def __init__(
        self, vocabulary, cache=True, cache_ttl=3600, service_id=None, id_field="id"
    ):
        """Initialize the labels.

        :param vocabulary: the name of the vocabulary type.
        :param cache: use simple process in-memory cache when True.
        :param cache_ttl: cache expiration in seconds.
        :param service_id: the name of the registered service to be used
            when fetching values for the vocabulary.
        :param id_field: the name of the `id` field.
        """
        self.vocabulary = vocabulary
        self.cache = cache
        self.cache_ttl = cache_ttl
        self._fields = ("id", "title")  # not configurable
        self.service_id = service_id
        self.id_field = id_field
        # init cache
        self._cache_key = (service_id, vocabulary)
        cached_labels.setdefault(self._cache_key, {})
        cached_labels_ttl.setdefault(self._cache_key, {})

    def _vocab_to_label(self, vocab):
        """Returns the label string for a vocabulary entry."""
        return lazy_get_label(vocab["title"])

    def __call__(self, ids):
        """Return the mapping when evaluated."""
        if not ids:
            return {}

        print(100*"*")
        try:
            if self.cache:
                print("cached")
                now = time.time()
                missing = set(ids).difference(set(cached_labels[self._cache_key].keys()))
                missing_vocabs = get_vocabs(self.service_id, self.vocabulary, self._fields, missing)
                for vocab in missing_vocabs:
                    id_ = vocab[self.id_field]
                    # print(f"++ label: {self._vocab_to_label(vocab)}")
                    cached_labels[self._cache_key][id_] = self._vocab_to_label(vocab)
                # set when these keys have been added
                cached_labels_ttl[self._cache_key][now] = missing
                # expire old keys
                one_hour_ago = now - self.cache_ttl
                expired_times = [_t for _t in cached_labels_ttl[self._cache_key].keys() if _t < one_hour_ago]
                for expired_time in expired_times:
                    ids_ = cached_labels_ttl[self._cache_key][expired_time]
                    for id_ in ids_:
                        cached_labels[self._cache_key].pop(id_, None)
                    cached_labels_ttl[self._cache_key].pop(expired_time, None)


                # check keys to expire
                delta = time.time() - now
                print("++ checking cache for ids: {ids}")
                print(f"++ missing: {missing}")
                print(f"{delta.seconds}.{delta.microseconds}")
                return cached_labels[self._cache_key]
            else:
                print("NOT cached")
                now = time.time()
                vocab_list = get_vocabs(
                    self.service_id,
                    self.vocabulary,
                    self._fields,
                    ids,
                )
                labels = {}
                for vocab in vocab_list:
                    id_ = vocab[self.id_field]
                    labels[id_] = self._vocab_to_label(vocab)
                delta = time.time() - now
                print(f"{delta.seconds}.{delta.microseconds}")
                return labels
        except NoResultFound:
            raise FacetNotFoundError(self.vocabulary)

        labels = {}
        ids = set(ids)
        seen = set()
        for vocab in vocab_list:
            # cannot loop over ids because vocab id is inside each item
            if len(ids) == len(seen):
                break

            id_ = vocab[self.id_field]
            if id_ in ids:
                labels[id_] = self._vocab_to_label(vocab)
                seen.add(id_)

        return labels
