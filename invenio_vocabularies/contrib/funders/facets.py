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

    def __init__(self, vocabulary, cache=False, service_name=None):
        """Initialize the labels."""
        super().__init__(
            vocabulary,
            cache,
            service_name="funders",
        )
        self.fields = ["id", "title", "country"]  # not configurable

    def _vocab_to_label(self, vocab):
        """Returns the label string for a vocabulary entry."""
        return f"{lazy_get_label(vocab['title'])} ({vocab['country']})"
