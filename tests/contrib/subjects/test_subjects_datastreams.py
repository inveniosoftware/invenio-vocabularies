# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 University of Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Subject datastream tests."""

from copy import deepcopy

import pytest
from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry

from invenio_vocabularies.contrib.subjects.api import Subject
from invenio_vocabularies.contrib.subjects.datastreams import SubjectsServiceWriter
from invenio_vocabularies.datastreams import StreamEntry
from invenio_vocabularies.datastreams.errors import WriterError


@pytest.fixture(scope="module")
def dict_subject_entry():
    return StreamEntry(
        {
            "title": {
                "en": "Dark Web",
                "de": "Darknet",
                "fr": "Réseaux anonymes (informatique)",
            },
            "id": "http://d-nb.info/gnd/1062531973",
            "scheme": "GND",
            "synonyms": ["Deep Web"],
        },
    )


def test_subjects_service_writer_create(app, db, search_clear, dict_subject_entry):
    writer = SubjectsServiceWriter()
    record = writer.write(dict_subject_entry)
    record = record.entry.to_dict()

    assert dict(record, **dict_subject_entry.entry) == record


def test_subjects_service_writer_duplicate(app, db, search_clear, dict_subject_entry):
    writer = SubjectsServiceWriter()
    _ = writer.write(stream_entry=dict_subject_entry)
    Subject.index.refresh()  # refresh index to make changes live
    with pytest.raises(WriterError) as err:
        writer.write(stream_entry=dict_subject_entry)

    expected_error = [f"Vocabulary entry already exists: {dict_subject_entry.entry}"]
    assert expected_error in err.value.args


def test_subjects_service_writer_update_existing(
    app, db, search_clear, dict_subject_entry
):
    # create vocabulary
    writer = SubjectsServiceWriter(update=True)
    subject = writer.write(stream_entry=dict_subject_entry)
    Subject.index.refresh()  # refresh index to make changes live
    # update vocabulary
    updated_subject = deepcopy(dict_subject_entry.entry)
    updated_subject["scheme"] = "new_scheme"
    del updated_subject["synonyms"]
    # check changes vocabulary
    _ = writer.write(stream_entry=StreamEntry(updated_subject))
    service = current_service_registry.get("subjects")
    record = service.read(system_identity, subject.entry.id)
    record = record.to_dict()

    # needed while the writer resolves from ES
    assert _.entry.id == subject.entry.id
    assert dict(record, **updated_subject) == record


def test_subjects_service_writer_update_non_existing(
    app, db, search_clear, dict_subject_entry
):
    # vocabulary item not created, call update directly
    updated_subject = deepcopy(dict_subject_entry.entry)
    updated_subject["scheme"] = "new_scheme"
    del updated_subject["synonyms"]
    # check changes vocabulary
    writer = SubjectsServiceWriter(update=True)
    subject = writer.write(stream_entry=StreamEntry(updated_subject))
    service = current_service_registry.get("subjects")
    record = service.read(system_identity, subject.entry.id)
    record = record.to_dict()

    assert dict(record, **updated_subject) == record
