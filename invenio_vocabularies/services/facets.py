# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2023 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary facets."""

from flask_principal import AnonymousIdentity
from invenio_cache.decorators import cached_with_expiration
from invenio_i18n.ext import current_i18n
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services.errors import FacetNotFoundError
from marshmallow_utils.fields.babel import gettext_from_dict
from speaklater import make_lazy_string
from sqlalchemy.exc import NoResultFound

from ..proxies import current_service


def get_service(service_id):
    """Get the service object by name.

    It is required to access the registry lazily, to avoid "out of
    application context" errors.
    """
    return current_service_registry.get(service_id) if service_id else current_service


def get_vocabs(service_id, type, fields, ids):
    """Fetch vocabulary values by ids, using the service."""
    service = get_service(service_id)
    vocabs = service.read_many(
        AnonymousIdentity(), type=type, ids=list(ids), fields=list(fields)
    )
    return list(vocabs.hits)  # the service returns a generator


@cached_with_expiration
def get_cached_vocab(service_id, type, fields, id_):
    """Cache vocabulary values by type in-memory."""
    vocabs = get_vocabs(service_id, type, fields, [id_])
    return vocabs[0] if vocabs else None


def lazy_get_label(vocab_item):
    """Lazy evaluation of a localized vocabulary label."""
    params = {"locale": current_i18n.locale, "default_locale": "en"}

    return make_lazy_string(gettext_from_dict, vocab_item, **params)


class VocabularyLabels:
    """Fetching of vocabulary labels for facets."""

    def __init__(
        self, vocabulary, cache=True, cache_ttl=3600, service_id=None, id_field="id"
    ):
        """Initialize the labels.

        :param vocabulary: the name of the vocabulary type.
        :param cache: use simple process in-memory cache when True.
        :param cache_ttl: cache expiration in seconds.
        :param service_id: the id of the registered service to be used
            when fetching values for the vocabulary.
        :param id_field: the name of the `id` field.
        """
        self.vocabulary = vocabulary
        self.cache = cache
        self.cache_ttl = cache_ttl
        self.fields = ("id", "title")  # not configurable
        self.service_id = service_id
        self.id_field = id_field

    def _vocab_to_label(self, vocab):
        """Returns the label string for a vocabulary entry."""
        return lazy_get_label(vocab["title"])

    def __call__(self, ids):
        """Return the mapping when evaluated."""
        if not ids:
            return {}

        labels = {}
        try:
            if self.cache:
                for id_ in ids:
                    vocab = get_cached_vocab(
                        self.service_id,
                        self.vocabulary,
                        self.fields,
                        id_,
                        cache_ttl=self.cache_ttl,
                    )
                    if not vocab:
                        continue
                    labels[vocab[self.id_field]] = self._vocab_to_label(vocab)
            else:
                vocab_list = get_vocabs(
                    self.service_id,
                    self.vocabulary,
                    self.fields,
                    ids,
                )
                for vocab in vocab_list:
                    id_ = vocab[self.id_field]
                    if id_ in ids:
                        labels[id_] = self._vocab_to_label(vocab)
        except NoResultFound:
            raise FacetNotFoundError(self.vocabulary)

        return labels
