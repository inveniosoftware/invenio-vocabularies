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


def get_service(service_name):
    """Get the service object by name.

    It is required to access the registry lazily, to avoid out of
    application context errors.
    """
    return (
        current_service_registry.get(service_name) if service_name else current_service
    )


def get_vocabs(service_name, type, ids, fields):
    """Fetch vocabulary values by ids, using the service."""
    service = get_service(service_name)
    vocabs = service.read_many(AnonymousIdentity(), type=type, ids=ids, fields=fields)
    return list(vocabs.hits)  # the service returns a generator


def get_ttl_hash(seconds=3600):
    """Return the same value withing `seconds` time period. Default 1 hour."""
    return round(time.time() / seconds)


@lru_cache(maxsize=32)
def cached_vocabs(service_name, type, ids, fields, ttl_hash=None):
    """Cache vocabulary values by type with a simple process in-memory cache.

    This cache is meant to greatly optimize performance when getting the title of
    each facet, during searches, and to avoid accessing DB/Search each time.
    This cache suffer of a slower warm up at the first cache miss when each process is
    restarted. A data store cache could be also used as mitigation, with the drawback
    of the added network latency.

    `@lru_cache` is threadsafe. `maxsize` is set to 32, assuming that there are not more
    than 32 (multiple of 2 for optimization) different vocabularies types defined
    in the instance.

    The ttl_hash kwarg is necessary to make the cache expiring, by changing the hash key
    after the defined time.
    """
    return get_vocabs(service_name, type=type, ids=list(ids), fields=list(fields))


def lazy_get_label(vocab_item):
    """Lazy evaluation of a localized vocabulary label."""
    params = {"locale": current_i18n.locale, "default_locale": "en"}

    return make_lazy_string(gettext_from_dict, vocab_item, **params)


class VocabularyLabels:
    """Fetching of vocabulary labels for facets."""

    def __init__(
        self, vocabulary, cache=True, cache_ttl=3600, service_name=None, id_field="id"
    ):
        """Initialize the labels.

        :param vocabulary: the name of the vocabulary type.
        :param cache: use simple process in-memory cache when True.
        :param cache_ttl: cache expiration in seconds.
        :param service_name: the name of the registered service to be used
            when fetching values for the vocabulary.
        :param id_field: the name of the `id` field.
        """
        self.vocabulary = vocabulary
        self.cache = cache
        self.cache_ttl = cache_ttl
        self.fields = ("id", "title")  # not configurable
        self.service_name = service_name
        self.id_field = id_field

    def _vocab_to_label(self, vocab):
        """Returns the label string for a vocabulary entry."""
        return lazy_get_label(vocab["title"])

    def __call__(self, ids):
        """Return the mapping when evaluated."""
        try:
            if self.cache:
                vocab_list = cached_vocabs(
                    self.service_name,
                    self.vocabulary,
                    tuple(ids),
                    self.fields,
                    ttl_hash=get_ttl_hash(seconds=self.cache_ttl),
                )
            else:
                vocab_list = get_vocabs(
                    self.service_name,
                    self.vocabulary,
                    ids,
                    list(self.fields),
                )
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
