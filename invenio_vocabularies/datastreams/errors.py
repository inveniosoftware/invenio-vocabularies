# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-License-Identifier: MIT

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
