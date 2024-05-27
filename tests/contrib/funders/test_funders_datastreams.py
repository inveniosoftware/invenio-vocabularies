# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
# Copyright (C) 2024 California Institute of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Funders datastreams tests."""

from copy import deepcopy

import pytest
from invenio_access.permissions import system_identity

from invenio_vocabularies.contrib.funders.api import Funder
from invenio_vocabularies.contrib.funders.datastreams import FundersServiceWriter
from invenio_vocabularies.datastreams import StreamEntry
from invenio_vocabularies.datastreams.errors import WriterError


def test_funders_service_writer_create(app, search_clear, funder_full_data):
    writer = FundersServiceWriter()
    funder_rec = writer.write(StreamEntry(funder_full_data))
    funder_dict = funder_rec.entry.to_dict()
    assert dict(funder_dict, **funder_full_data) == funder_dict

    # not-ideal cleanup
    funder_rec.entry._record.delete(force=True)


def test_funders_service_writer_duplicate(app, search_clear, funder_full_data):
    writer = FundersServiceWriter()
    funder_rec = writer.write(stream_entry=StreamEntry(funder_full_data))
    Funder.index.refresh()  # refresh index to make changes live
    with pytest.raises(WriterError) as err:
        writer.write(stream_entry=StreamEntry(funder_full_data))

    expected_error = [f"Vocabulary entry already exists: {funder_full_data}"]
    assert expected_error in err.value.args

    # not-ideal cleanup
    funder_rec.entry._record.delete(force=True)


def test_funders_service_writer_update_existing(
    app, search_clear, funder_full_data, service
):
    # create vocabulary
    writer = FundersServiceWriter(update=True)
    orig_funder_rec = writer.write(stream_entry=StreamEntry(funder_full_data))
    Funder.index.refresh()  # refresh index to make changes live
    # update vocabulary
    updated_funder = deepcopy(funder_full_data)
    updated_funder["name"] = "Updated Name"
    # check changes vocabulary
    _ = writer.write(stream_entry=StreamEntry(updated_funder))
    funder_rec = service.read(system_identity, orig_funder_rec.entry.id)
    funder_dict = funder_rec.to_dict()

    # needed while the writer resolves from ES
    assert _.entry.id == orig_funder_rec.entry.id
    assert dict(funder_dict, **updated_funder) == funder_dict

    # not-ideal cleanup
    funder_rec._record.delete(force=True)


def test_funders_service_writer_update_non_existing(
    app, search_clear, funder_full_data, service
):
    # vocabulary item not created, call update directly
    updated_funder = deepcopy(funder_full_data)
    updated_funder["name"] = "New name"
    # check changes vocabulary
    writer = FundersServiceWriter(update=True)
    funder_rec = writer.write(stream_entry=StreamEntry(updated_funder))
    funder_rec = service.read(system_identity, funder_rec.entry.id)
    funder_dict = funder_rec.to_dict()

    assert dict(funder_dict, **updated_funder) == funder_dict

    # not-ideal cleanup
    funder_rec._record.delete(force=True)
