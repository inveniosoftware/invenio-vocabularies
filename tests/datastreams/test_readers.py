# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Data Streams readers tests."""
import json
import tarfile
from pathlib import Path

import pytest
import yaml

from invenio_vocabularies.datastreams.readers import (
    JsonReader,
    TarReader,
    YamlReader,
    ZipReader,
)


@pytest.fixture(scope="module")
def expected_from_yaml():
    return [{"test": {"inner": "value"}}, {"test": {"inner": "value"}}]


@pytest.fixture(scope="function")
def yaml_file(expected_from_yaml):
    filename = Path("reader_test.yaml")
    with open(filename, "w") as file:
        yaml.dump(expected_from_yaml, file)

    yield filename

    filename.unlink()  # delete created file


def test_yaml_reader(yaml_file, expected_from_yaml):
    reader = YamlReader(yaml_file)

    for idx, data in enumerate(reader.read()):
        assert data == expected_from_yaml[idx]


@pytest.fixture(scope="module")
def expected_from_tar():
    return {"test": {"inner": "value"}}


@pytest.fixture(scope="function")
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
            with open(inner_filename, "w") as file:
                yaml.dump(expected_from_tar, file)
                tar.add(inner_filename)
            inner_filename.unlink()

    yield filename

    filename.unlink()  # delete created file


def test_tar_reader(tar_file, expected_from_tar):
    reader = TarReader(tar_file, regex=".yaml$")

    total = 0
    for data in reader.read():
        assert yaml.safe_load(data) == expected_from_tar
        total += 1

    assert total == 2  # ignored the `.other` file


def test_zip_reader(zip_file, json_list):
    reader = ZipReader(zip_file, regex=".json$")
    total = 0
    for data in reader.read():
        assert json.load(data) == json_list
        total += 1

    assert total == 2  # ignored the `.other` file


@pytest.fixture(scope="function")
def json_list_file(json_list):
    """Creates a JSON file with an array inside."""
    filename = Path("reader_test.json")
    with open(filename, mode="w") as file:
        json.dump(json_list, file)

    yield filename

    filename.unlink()  # delete created file


def test_json_list_reader(json_list_file, json_element):
    reader = JsonReader(json_list_file, regex=".json$")

    for count, data in enumerate(reader.read(), start=1):
        assert data == json_element

    assert count == 2


@pytest.fixture(scope="function")
def json_element_file(json_element):
    """Creates a JSON file with only one element inside."""
    filename = Path("reader_test.json")
    with open(filename, mode="w") as file:
        json.dump(json_element, file)
    yield filename
    filename.unlink()  # delete created file


def test_json_element_reader(json_element_file, json_element):
    reader = JsonReader(json_element_file, regex=".json$")

    for count, data in enumerate(reader.read(), start=1):
        assert data == json_element

    assert count == 1


# FIXME: add test for csv reader
