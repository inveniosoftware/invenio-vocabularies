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


@pytest.fixture(scope='module')
def app_config(app_config):
    """Mimic an instance's configuration."""
    app_config["VOCABULARIES_DATASTREAM_READERS"] = {
        "test": BaseReader
    }
    app_config["VOCABULARIES_DATASTREAM_TRANSFORMERS"] = {
        "test": BaseTransformer
    }
    app_config["VOCABULARIES_DATASTREAM_WRITERS"] = {
        "test": BaseWriter
    }

    return app_config


def test_read(*args, **kwargs):
    yield StreamEntry({})


def test_apply(*args, **kwargs):
    return StreamEntry({})


def test_write(*args, **kwargs):
    return StreamEntry(entry={}, errors=[])


@patch(
    'invenio_vocabularies.datastreams.readers.BaseReader.read',
    side_effect=test_read
)
@patch(
    'invenio_vocabularies.datastreams.transformers.BaseTransformer.apply',
    side_effect=test_apply
)
@patch(
    'invenio_vocabularies.datastreams.writers.BaseWriter.write',
    side_effect=test_write
)
def test_task_creation(
    p_read, p_apply, p_write, app, client_with_credentials, h
):
    client = client_with_credentials
    task_config = {
        "reader": {
            "type": "test",
            "args": {
                "origin": "somewhere"
            }
        },
        "transformers": [{"type": "test"}],
        "writers": [{"type": "test"}]
    }

    resp = client.post(
        "/vocabularies/tasks", headers=h, data=json.dumps(task_config)
    )
    assert resp.status_code == 202
    p_read.assert_called()
    p_apply.assert_called()
    p_write.assert_called()
