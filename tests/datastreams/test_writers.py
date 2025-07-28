# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Data Streams writers tests."""

from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from invenio_vocabularies.datastreams import StreamEntry
from invenio_vocabularies.datastreams.errors import WriterError
from invenio_vocabularies.datastreams.writers import (
    AsyncWriter,
    ServiceWriter,
    YamlWriter,
)

##
# Service Writer
##


def test_service_writer_non_existing(lang_type, lang_data, service, identity):
    writer = ServiceWriter(service, identity=identity)
    lang = writer.write(stream_entry=StreamEntry(lang_data))
    record = service.read(identity, ("languages", lang.entry.id))
    record = record.to_dict()

    assert dict(record, **lang_data) == record


def test_service_writer_duplicate(lang_type, lang_data, service, identity):
    writer = ServiceWriter(service, identity=identity)
    _ = writer.write(stream_entry=StreamEntry(lang_data))
    with pytest.raises(WriterError) as err:
        writer.write(stream_entry=StreamEntry(lang_data))

    expected_error = [f"Vocabulary entry already exists: {lang_data}"]
    assert expected_error in err.value.args


def test_service_writer_update_existing(lang_type, lang_data, service, identity):
    # create vocabulary
    writer = ServiceWriter(service, identity=identity, update=True)
    lang = writer.write(stream_entry=StreamEntry(lang_data))
    # update vocabulary
    updated_lang = deepcopy(lang_data)
    updated_lang["description"]["en"] = "Updated english description"
    updated_lang["tags"].append("updated")
    # check changes vocabulary
    _ = writer.write(stream_entry=StreamEntry(updated_lang))
    record = service.read(identity, ("languages", lang.entry.id))
    record = record.to_dict()

    assert dict(record, **updated_lang) == record


def test_service_writer_update_non_existing(lang_type, lang_data, service, identity):
    # vocabulary item not created, call update directly
    updated_lang = deepcopy(lang_data)
    updated_lang["description"]["en"] = "Updated english description"
    updated_lang["tags"].append("updated")
    # check changes vocabulary
    writer = ServiceWriter(service, identity=identity, update=True)
    lang = writer.write(stream_entry=StreamEntry(updated_lang))
    record = service.read(identity, ("languages", lang.entry.id))
    record = record.to_dict()

    assert dict(record, **updated_lang) == record


def test_writer_wrong_config_no_insert_no_update(
    lang_type, lang_data, service, identity
):
    writer = ServiceWriter(service, identity=identity, insert=False, update=False)

    with pytest.raises(WriterError) as err:
        writer.write(stream_entry=StreamEntry(lang_data))

    expected_error = ["Writer wrongly configured to not insert and to not update"]
    assert expected_error in err.value.args


def test_writer_no_insert(lang_type, lang_data, service, identity):
    writer = ServiceWriter(service, identity=identity, insert=False, update=True)

    with pytest.raises(WriterError) as err:
        writer.write(stream_entry=StreamEntry(lang_data))

    expected_error = [f"Vocabulary entry does not exist: {lang_data}"]
    assert expected_error in err.value.args


##
# YAML Writer
##


def test_yaml_writer():
    filepath = Path("writer_test.yaml")
    test_output = [{"key_one": [{"inner_one": 1}]}, {"key_two": [{"inner_two": "two"}]}]

    writer = YamlWriter(filepath=filepath)
    for output in test_output:
        writer.write(stream_entry=StreamEntry(output))

    with open(filepath) as file:
        assert yaml.safe_load(file) == test_output

    filepath.unlink()


##
# Async Writer
##


def test_async_writer():
    """Test AsyncWriter calls celery task with correct args."""
    dummy_writer = MagicMock()
    stream_entry_1 = StreamEntry({"key_one": [{"inner_one": 1}]})
    stream_entry_2 = StreamEntry({"key_two": [{"inner_two": "two"}]})
    writer = AsyncWriter(writer=dummy_writer)

    with patch(
        "invenio_vocabularies.datastreams.writers.write_entry.apply_async"
    ) as mock_write_entry:
        writer.write(stream_entry_1, subtask_run_id="run-1")
        mock_write_entry.assert_called_once()
        _, kwargs = mock_write_entry.call_args
        assert kwargs["args"][0] == dummy_writer
        assert kwargs["args"][1] == stream_entry_1.entry
        assert kwargs["args"][2] == "run-1"
        assert kwargs["countdown"] == 1

    with patch(
        "invenio_vocabularies.datastreams.writers.write_many_entry.apply_async"
    ) as mock_write_many_entry:
        writer.write_many([stream_entry_1, stream_entry_2], subtask_run_id="run-2")
        mock_write_many_entry.assert_called_once()
        _, kwargs = mock_write_many_entry.call_args
        assert kwargs["args"][0] == dummy_writer
        assert kwargs["args"][1] == [stream_entry_1.entry, stream_entry_2.entry]
        assert kwargs["args"][2] == "run-2"
        assert kwargs["countdown"] == 1
