# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Data Streams readers tests."""

import tarfile
from pathlib import Path

import pytest
import yaml

from invenio_vocabularies.datastreams.readers import TarReader, YamlReader


@pytest.fixture(scope='module')
def expected_from_yaml():
    return [
        {
            "test": {
                "inner": "value"
            }
        }, {
            "test": {
                "inner": "value"
            }
        }
    ]


@pytest.fixture(scope='function')
def yaml_file(expected_from_yaml):
    filename = Path('reader_test.yaml')
    with open(filename, 'w') as file:
        yaml.dump(expected_from_yaml, file)

    yield filename

    filename.unlink()  # delete created file


def test_yaml_reader(yaml_file, expected_from_yaml):
    reader = YamlReader(yaml_file)

    for idx, stream_entry in enumerate(reader.read()):
        assert stream_entry.entry == expected_from_yaml[idx]


@pytest.fixture(scope='module')
def expected_from_tar():
    return {
        "test": {
            "inner": "value"
        }
    }


@pytest.fixture(scope='function')
def tar_file(expected_from_tar):
    """Creates a Tar file with three files (two yaml) inside.

    Each iteration should return the content of one yaml file,
    it should ignore the .other file.
    """
    files = ["file_one.yaml", "file_two.yaml", "file_three.other"]
    filename = Path("reader_test.tar.gz")
    with tarfile.open(filename, "w:gz") as tar:
        for file_ in files:
            inner_filename = Path(file_)
            with open(inner_filename, 'w') as file:
                yaml.dump(expected_from_tar, file)
                tar.add(inner_filename)
            inner_filename.unlink()

    yield filename

    filename.unlink()  # delete created file


def test_tar_reader(tar_file, expected_from_tar):
    reader = TarReader(tar_file, regex=".yaml$")

    total = 0
    for stream_entry in reader.read():
        assert yaml.safe_load(stream_entry.entry) == expected_from_tar
        total += 1

    assert total == 2  # ignored the `.other` file
