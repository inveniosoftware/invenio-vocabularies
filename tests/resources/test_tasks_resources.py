# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Tasks REST API tests."""

import json
from unittest.mock import patch

import pytest

from invenio_vocabularies.datastreams.datastreams import StreamEntry
from invenio_vocabularies.datastreams.readers import BaseReader
from invenio_vocabularies.datastreams.transformers import BaseTransformer
from invenio_vocabularies.datastreams.writers import BaseWriter


class TestReader(BaseReader):
    """Test reader."""

    # needs implementation due to abstract decorator in the base class
    def _iter(self, fp, *args, **kwargs):
        pass

    def read(self, item=None, *args, **kwargs):
        """Reads from item or opens the file descriptor from origin."""
        yield 1


class TestTransformer(BaseTransformer):
    """Test transformer."""

    # no need for self since it is patched
    def apply(stream_entry, *args, **kwargs):
        """Forwards entry."""
        return stream_entry


class TestWriter(BaseWriter):
    """Test writer."""

    # no need for self since it is patched
    def write(stream_entry, *args, **kwargs):
        """NOP write."""
        pass


@pytest.fixture(scope="module")
def app_config(app_config):
    """Mimic an instance's configuration."""
    app_config["VOCABULARIES_DATASTREAM_READERS"] = {"test": TestReader}
    app_config["VOCABULARIES_DATASTREAM_TRANSFORMERS"] = {"test": TestTransformer}
    app_config["VOCABULARIES_DATASTREAM_WRITERS"] = {"test": TestWriter}

    return app_config


def test_task_creation(app, client_with_credentials, h):
    client = client_with_credentials
    task_config = {
        "readers": [{"type": "test", "args": {"origin": "somewhere"}}],
        "transformers": [{"type": "test"}],
        "writers": [{"type": "test"}],
    }

    with patch.object(
        TestReader, "read", side_effect=TestReader.read
    ) as p_read, patch.object(
        TestTransformer, "apply", side_effect=TestTransformer.apply
    ) as p_apply, patch.object(
        TestWriter, "write", side_effect=TestWriter.write
    ) as p_write:
        resp = client.post(
            "/vocabularies/tasks", headers=h, data=json.dumps(task_config)
        )
        assert resp.status_code == 202
        p_read.assert_called()
        p_apply.assert_called()
        p_write.assert_called()
