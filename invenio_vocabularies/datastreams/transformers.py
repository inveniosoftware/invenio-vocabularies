# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Transformers module."""


class BaseTransformer:
    """Base transformer."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        pass

    def apply(self, entry, *args, **kwargs):
        """Applies the transformation to the entry.

        :returns: The transformed entry, this allow them to be chained
                  raises TransformerError in case of errors.
        """
        pass
