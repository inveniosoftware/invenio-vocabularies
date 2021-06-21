# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary facets."""

from flask_principal import AnonymousIdentity
from invenio_i18n.ext import current_i18n
from marshmallow_utils.fields.babel import gettext_from_dict
from speaklater import make_lazy_string

from ..proxies import current_service


def lazy_get_label(vocab_item):
    """Lazy evaluation of a localized vocabulary label."""
    params = {
        "locale": current_i18n.locale,
        "default_locale": "en"
    }

    return make_lazy_string(
        gettext_from_dict, vocab_item, **params)


class VocabularyLabels:
    """Fetching of vocabulary labels for facets."""

    def __init__(self, vocabulary, cache=False):
        """Initialize the labels."""
        self.vocabulary = vocabulary
        self.cache = cache
        self.fields = ["id", "title"]  # not configurable

    def __call__(self, ids):
        """Return the mapping when evaluated."""
        identity = AnonymousIdentity()
        if not self.cache:
            vocabs = current_service.read_many(
                identity, type=self.vocabulary, ids=ids, fields=self.fields)
        else:
            vocabs = current_service.read_all(
                identity, type=self.vocabulary, fields=self.fields)

        labels = {}
        vocab_list = list(vocabs.hits)  # the service returns a generator
        ids = set(ids)
        seen = set()
        for vocab in vocab_list:
            # cannot loop over ids because vocab id is inside each item
            if len(ids) == len(seen):
                break

            id_ = vocab["id"]
            if id_ in ids:
                labels[id_] = lazy_get_label(vocab["title"])
                seen.add(id_)

        return labels
