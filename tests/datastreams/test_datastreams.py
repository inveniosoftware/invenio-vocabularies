# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""DataStreams tests."""

import json
import zipfile
from pathlib import Path

import pytest

from invenio_vocabularies.datastreams.factories import DataStreamFactory


@pytest.fixture(scope="module")
def vocabulary_config():
    """Parsed vocabulary configuration."""
    return {
        "transformers": [{"type": "test"}],
        "readers": [
            {
                "type": "test",
                "args": {
                    "origin": [1, -1],
                },
            }
        ],
        "writers": [{"type": "test"}],
    }


def test_base_datastream(app, vocabulary_config):
    datastream = DataStreamFactory.create(
        readers_config=vocabulary_config["readers"],
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
    custom_config["writers"].append(
        {
            "type": "fail",
            "args": {"fail_on": 2},  # 2 means 1 as entry cuz transformers sums 1
        }
    )

    datastream = DataStreamFactory.create(
        readers_config=vocabulary_config["readers"],
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


@pytest.fixture(scope="function")
def zip_file(json_list):
    """Creates a Zip file with three files inside.

    The first file should return two json elements.
    The second file should fail.
    The third file should return two json elements.
    """

    def _correct_file(archive, idx):
        correct_file = Path(f"correct_{idx}.json")
        with open(correct_file, "w") as file:
            json.dump(json_list, file)
        archive.write(correct_file)
        correct_file.unlink()

    filename = Path("reader_test.zip")
    with zipfile.ZipFile(file=filename, mode="w") as archive:
        _correct_file(archive, 1)
        errored_file = Path("errored.json")
        with open(errored_file, "w") as file:
            file.write(  # to dump incorrect json format
                # missing comma and closing bracket
                '[{"test": {"inner": "value"}{"test": {"inner": "value"}}]'
            )
        archive.write(errored_file)
        _correct_file(archive, 2)
        errored_file.unlink()

    yield filename

    filename.unlink()  # delete created file


def test_piping_readers(app, zip_file, json_element):
    ds_config = {
        "readers": [
            {
                "type": "zip",
                "args": {
                    "origin": "reader_test.zip",
                    "regex": ".json$",
                },
            },
            {"type": "json"},
        ],
        "writers": [{"type": "test"}],
    }

    datastream = DataStreamFactory.create(
        readers_config=ds_config["readers"],
        writers_config=ds_config["writers"],
    )
    expected_errors = [
        "ZipReader.read: Cannot decode JSON file errored.json: Expecting ',' delimiter: line 1 column 29 (char 28)"  # noqa
    ]

    iter = datastream.process()
    for count, entry in enumerate(iter, start=1):
        if count != 3:
            assert entry.entry == json_element
        else:
            # assert the second file fails
            assert entry.entry.name == "errored.json"
            assert entry.errors == expected_errors

    assert count == 5  # 2 good + 1 bad + 2 good
