# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-License-Identifier: MIT

"""Datastream errors."""


class ReaderError(Exception):
    """Transformer application exception."""


class IncompleteReadError(Exception):
    """Reader ran out of data before it got everything it expected.

    Example: INSPIRE said there were 100 records, we only managed to pull 90.
    Whatever we already handed to the stream should still be written, but the
    job must end as a partial success so someone notices the gap.

    This is intentionally not a ``ReaderError``. DataStream treats
    ``ReaderError`` as "skip this one entry and keep going". An incomplete
    read is about the whole run, so it has to bubble up instead.
    """


class TransformerError(Exception):
    """Transformer application exception."""


class WriterError(Exception):
    """Transformer application exception."""


class FactoryError(Exception):
    """Transformer application exception."""

    def __init__(self, name, key):
        """Initialise error."""
        super().__init__(f"{name} {key} not configured.")
