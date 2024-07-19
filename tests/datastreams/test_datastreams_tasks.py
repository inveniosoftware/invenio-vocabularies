# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Data Streams tasks tests."""

from pathlib import Path

import yaml

from invenio_vocabularies.datastreams.tasks import write_entry, write_many_entry


def test_write_entry(app):
    filepath = "writer_test.yaml"
    yaml_writer_config = {"type": "yaml", "args": {"filepath": filepath}}
    entry = {"key_one": [{"inner_one": 1}]}
    write_entry(yaml_writer_config, entry)

    filepath = Path(filepath)
    with open(filepath) as file:
        assert yaml.safe_load(file) == [entry]

    filepath.unlink()


def test_write_many_entry(app):
    filepath = "writer_test.yaml"
    yaml_writer_config = {"type": "yaml", "args": {"filepath": filepath}}
    entries = [{"key_one": [{"inner_one": 1}]}, {"key_two": [{"inner_two": 2}]}]
    write_many_entry(yaml_writer_config, entries)

    filepath = Path(filepath)
    with open(filepath) as file:
        assert yaml.safe_load(file) == entries

    filepath.unlink()
