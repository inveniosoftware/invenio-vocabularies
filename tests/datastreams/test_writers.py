# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Data Streams writers tests."""

from pathlib import Path

import yaml

from invenio_vocabularies.datastreams.writers import ServiceWriter, YamlWriter


def test_service_writer(lang_type, lang_data, service, identity):
    writer = ServiceWriter(service, identity)
    lang = writer.write(entry=lang_data)
    record = service.read(identity, ("languages", lang.id))
    record = record.to_dict()

    assert dict(record, **lang_data) == record


def test_yaml_writer():
    filepath = Path('writer_test.yaml')
    test_output = [
        {"key_one": [{"inner_one": 1}]},
        {"key_two": [{"inner_two": "two"}]}
    ]

    writer = YamlWriter(filepath=filepath)
    for output in test_output:
        assert not writer.write(entry=output).errors

    with open(filepath) as file:
        assert yaml.safe_load(file) == test_output

    filepath.unlink()
