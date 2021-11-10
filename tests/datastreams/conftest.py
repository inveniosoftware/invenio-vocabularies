# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest

from invenio_vocabularies.datastreams.errors import TransformerError, \
    WriterError
from invenio_vocabularies.datastreams.readers import BaseReader
from invenio_vocabularies.datastreams.transformers import BaseTransformer
from invenio_vocabularies.datastreams.writers import BaseWriter


class TestReader(BaseReader):
    """Test reader."""

    def read(self, *args, **kwargs):
        """Yields the values in the origin."""
        for value in self._origin:
            yield value


class TestTransformer(BaseTransformer):
    """Test transformer."""

    def apply(self, entry, *args, **kwargs):
        """Sums up one to the value."""
        if entry < 0:
            raise TransformerError("Value cannot be negative")

        return entry + 1


class TestWriter(BaseWriter):
    """Test reader."""


class FailingTestWriter(BaseWriter):
    """Test reader."""

    def __init__(self, fail_on):
        """Initialise error."""
        super().__init__()
        self.fail_on = fail_on

    def write(self, entry):
        """Return the entry."""
        if entry == self.fail_on:
            raise WriterError(f"{self.fail_on} value found.")


@pytest.fixture(scope='module')
def app_config(app_config):
    """Mimic an instance's configuration."""
    app_config["VOCABULARIES_DATASTREAM_READERS"] = {
        "test": TestReader
    }
    app_config["VOCABULARIES_DATASTREAM_TRANSFORMERS"] = {
        "test": TestTransformer
    }
    app_config["VOCABULARIES_DATASTREAM_WRITERS"] = {
        "test": TestWriter,
        "fail": FailingTestWriter,
    }

    return app_config
