# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import json
import zipfile
from pathlib import Path

import pytest

from invenio_vocabularies.config import (
    VOCABULARIES_DATASTREAM_READERS,
    VOCABULARIES_DATASTREAM_TRANSFORMERS,
    VOCABULARIES_DATASTREAM_WRITERS,
)
from invenio_vocabularies.datastreams.errors import TransformerError, WriterError
from invenio_vocabularies.datastreams.readers import BaseReader, JsonReader, ZipReader
from invenio_vocabularies.datastreams.transformers import BaseTransformer
from invenio_vocabularies.datastreams.writers import BaseWriter


class TestReader(BaseReader):
    """Test reader."""

    def _iter(self, fp, *args, **kwargs):
        """Yields the values in the origin."""
        for value in self._origin:
            yield value

    def read(self, item=None, *args, **kwargs):
        """Reads from item or opens the file descriptor from origin."""
        yield from self._iter(fp=self._origin, *args, **kwargs)


class TestTransformer(BaseTransformer):
    """Test transformer."""

    def apply(self, stream_entry, *args, **kwargs):
        """Sums up one to the value."""
        if stream_entry.entry < 0:
            raise TransformerError("Value cannot be negative")

        stream_entry.entry += 1
        return stream_entry


class TestWriter(BaseWriter):
    """Test writer."""

    def write(self, stream_entry, *args, **kwargs):
        """NOP write."""
        pass

    def write_many(self, stream_entries, *args, **kwargs):
        """NOP write."""
        pass


class FailingTestWriter(BaseWriter):
    """Failing test writer."""

    def __init__(self, fail_on):
        """Initialise error."""
        super().__init__()
        self.fail_on = fail_on

    def write(self, stream_entry, *args, **kwargs):
        """Return the entry."""
        if stream_entry.entry == self.fail_on:
            raise WriterError(f"{self.fail_on} value found.")

    def write_many(self, stream_entries, *args, **kwargs):
        """NOP write."""
        pass


@pytest.fixture(scope="module")
def app_config(app_config):
    """Mimic an instance's configuration."""
    app_config["VOCABULARIES_DATASTREAM_READERS"] = {
        **VOCABULARIES_DATASTREAM_READERS,
        "test": TestReader,
    }
    app_config["VOCABULARIES_DATASTREAM_TRANSFORMERS"] = {
        **VOCABULARIES_DATASTREAM_TRANSFORMERS,
        "test": TestTransformer,
    }
    app_config["VOCABULARIES_DATASTREAM_WRITERS"] = {
        **VOCABULARIES_DATASTREAM_WRITERS,
        "test": TestWriter,
        "fail": FailingTestWriter,
    }

    return app_config


@pytest.fixture(scope="module")
def json_list():
    """Expected json list."""
    return [{"test": {"inner": "value"}}, {"test": {"inner": "value"}}]


@pytest.fixture(scope="module")
def json_element():
    """Expected json element."""
    return {"test": {"inner": "value"}}


@pytest.fixture(scope="function")
def zip_file(json_list):
    """Creates a Zip file with three files (two json) inside.

    Each iteration should return the content of one json file,
    it should ignore the .other file.
    """
    files = ["file_one.json", "file_two.json", "file_three.other"]
    filename = Path("reader_test.zip")
    with zipfile.ZipFile(file=filename, mode="w") as archive:
        for file_ in files:
            inner_filename = Path(file_)
            with open(inner_filename, "w") as file:
                json.dump(json_list, file)
            archive.write(inner_filename)
            inner_filename.unlink()

    yield filename

    filename.unlink()  # delete created file
