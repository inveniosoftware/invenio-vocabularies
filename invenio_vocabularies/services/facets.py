# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary facets."""

from flask_principal import AnonymousIdentity
from invenio_i18n.ext import current_i18n
from invenio_records_resources.proxies import current_service_registry
from invenio_records_resources.services.errors import FacetNotFoundError
from marshmallow_utils.fields.babel import gettext_from_dict
from speaklater import make_lazy_string
from sqlalchemy.exc import NoResultFound

from ..proxies import current_service


def lazy_get_label(vocab_item):
    """Lazy evaluation of a localized vocabulary label."""
    params = {"locale": current_i18n.locale, "default_locale": "en"}

    return make_lazy_string(gettext_from_dict, vocab_item, **params)


class VocabularyLabels:
    """Fetching of vocabulary labels for facets."""

    def __init__(self, vocabulary, cache=False, service_name=None, id_field="id"):
        """Initialize the labels."""
        self.vocabulary = vocabulary
        self.cache = cache
        self.fields = ["id", "title"]  # not configurable
        self.service_name = service_name
        self.id_field = id_field

    @property
    def service(self):
        """Service property.

        It is required to access the regitry lazily to avoid out of
        application context errors.
        """
        if not self.service_name:
            return current_service
        return current_service_registry.get(self.service_name)

    def _vocab_to_label(self, vocab):
        """Returns the label string for a vocabulary entry."""
        return lazy_get_label(vocab["title"])

    def __call__(self, ids):
        """Return the mapping when evaluated."""
        identity = AnonymousIdentity()
        try:
            if not self.cache:
                vocabs = self.service.read_many(
                    identity, type=self.vocabulary, ids=ids, fields=self.fields
                )
            else:
                vocabs = self.service.read_all(
                    identity, type=self.vocabulary, fields=self.fields
                )
        except NoResultFound:
            raise FacetNotFoundError(self.vocabulary)

        labels = {}
        vocab_list = list(vocabs.hits)  # the service returns a generator
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
