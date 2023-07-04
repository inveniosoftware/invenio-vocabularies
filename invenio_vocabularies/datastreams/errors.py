# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Datastream errors."""


class ReaderError(Exception):
    """Transformer application exception."""


class TransformerError(Exception):
    """Transformer application exception."""


class WriterError(Exception):
    """Transformer application exception."""


class FactoryError(Exception):
    """Transformer application exception."""

    def __init__(self, name, key):
        """Initialise error."""
        super().__init__(f"{name} {key} not configured.")
