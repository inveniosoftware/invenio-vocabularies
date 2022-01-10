# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""DataStreams tests."""

from pathlib import Path

import pytest

from invenio_vocabularies.datastreams.factories import DataStreamFactory


@pytest.fixture(scope="module")
def vocabulary_config():
    """Parsed vocabulary configuration."""
    return {
        "transformers": [
            {"type": "test"}
        ],
        "reader": {
            "type": "test",
            "args": {
                "origin": [1, -1],
            }
        },
        "writers": [
            {"type": "test"}
        ]
    }


def test_base_datastream(app, vocabulary_config):
    datastream = DataStreamFactory.create(
        reader_config=vocabulary_config["reader"],
        transformers_config=vocabulary_config.get("transformers"),
        writers_config=vocabulary_config["writers"],
    )

    stream_iter = datastream.process()
    valid = next(stream_iter)
    assert valid.entry == 2
    assert not valid.errors

    invalid = next(stream_iter)
    assert invalid.entry == -1
    assert "TestTransformer: Value cannot be negative" in invalid.errors


def test_base_datastream_fail_on_write(app, vocabulary_config):
    custom_config = dict(vocabulary_config)
    custom_config["writers"].append({
        "type": "fail",
        "args": {"fail_on": 2}  # 2 means 1 as entry cuz transformers sums 1
    })

    datastream = DataStreamFactory.create(
        reader_config=vocabulary_config["reader"],
        transformers_config=vocabulary_config.get("transformers"),
        writers_config=vocabulary_config["writers"],
    )

    stream_iter = datastream.process()
    invalid_wr = next(stream_iter)
    assert invalid_wr.entry == 2  # entry got transformed
    assert "FailingTestWriter: 2 value found." in invalid_wr.errors

    # failed on the previous but can process the next
    invalid_tr = next(stream_iter)
    assert invalid_tr.entry == -1
    assert "TestTransformer: Value cannot be negative" in invalid_tr.errors
