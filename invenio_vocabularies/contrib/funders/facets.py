# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary awards facets and labels."""

from ...services.facets import VocabularyLabels, lazy_get_label


class FundersLabels(VocabularyLabels):
    """Fetching of vocabulary labels for facets."""

    def __init__(self, vocabulary, cache=True, cache_ttl=3600, service_id=None):
        """Initialize the labels.

        :param vocabulary: the name of the vocabulary type.
        :param cache: use simple process in-memory cache when True.
        :param cache_ttl: cache expiration in seconds.
        :param service_id: the id of the registered service to be used
            when fetching values for the vocabulary.
        """
        super().__init__(
            vocabulary,
            cache=cache,
            cache_ttl=cache_ttl,
            service_id="funders",
        )
        self.fields = ("id", "title", "country")  # not configurable

    def _vocab_to_label(self, vocab):
        """Returns the label string for a vocabulary entry."""
        return f"{lazy_get_label(vocab['title'])} ({vocab['country']})"
