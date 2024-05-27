# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
# Copyright (C) 2024 California Institute of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Affiliations datastreams tests."""

from copy import deepcopy

import pytest
from invenio_access.permissions import system_identity

from invenio_vocabularies.contrib.affiliations.api import Affiliation
from invenio_vocabularies.contrib.affiliations.datastreams import (
    AffiliationsServiceWriter,
)
from invenio_vocabularies.datastreams import StreamEntry
from invenio_vocabularies.datastreams.errors import WriterError


def test_affiliations_service_writer_create(app, search_clear, affiliation_full_data):
    writer = AffiliationsServiceWriter()
    affiliation_rec = writer.write(StreamEntry(affiliation_full_data))
    affiliation_dict = affiliation_rec.entry.to_dict()
    assert dict(affiliation_dict, **affiliation_full_data) == affiliation_dict

    # not-ideal cleanup
    affiliation_rec.entry._record.delete(force=True)


def test_affiliations_service_writer_duplicate(
    app, search_clear, affiliation_full_data
):
    writer = AffiliationsServiceWriter()
    affiliation_rec = writer.write(stream_entry=StreamEntry(affiliation_full_data))
    Affiliation.index.refresh()  # refresh index to make changes live
    with pytest.raises(WriterError) as err:
        writer.write(stream_entry=StreamEntry(affiliation_full_data))

    expected_error = [f"Vocabulary entry already exists: {affiliation_full_data}"]
    assert expected_error in err.value.args

    # not-ideal cleanup
    affiliation_rec.entry._record.delete(force=True)


def test_affiliations_service_writer_update_existing(
    app, search_clear, affiliation_full_data, service
):
    # create vocabulary
    writer = AffiliationsServiceWriter(update=True)
    orig_affiliation_rec = writer.write(stream_entry=StreamEntry(affiliation_full_data))
    Affiliation.index.refresh()  # refresh index to make changes live
    # update vocabulary
    updated_affiliation = deepcopy(affiliation_full_data)
    updated_affiliation["name"] = "Updated Name"
    # check changes vocabulary
    _ = writer.write(stream_entry=StreamEntry(updated_affiliation))
    affiliation_rec = service.read(system_identity, orig_affiliation_rec.entry.id)
    affiliation_dict = affiliation_rec.to_dict()

    # needed while the writer resolves from ES
    assert _.entry.id == orig_affiliation_rec.entry.id
    assert dict(affiliation_dict, **updated_affiliation) == affiliation_dict

    # not-ideal cleanup
    affiliation_rec._record.delete(force=True)


def test_affiliations_service_writer_update_non_existing(
    app, search_clear, affiliation_full_data, service
):
    # vocabulary item not created, call update directly
    updated_affiliation = deepcopy(affiliation_full_data)
    updated_affiliation["name"] = "New name"
    # check changes vocabulary
    writer = AffiliationsServiceWriter(update=True)
    affiliation_rec = writer.write(stream_entry=StreamEntry(updated_affiliation))
    affiliation_rec = service.read(system_identity, affiliation_rec.entry.id)
    affiliation_dict = affiliation_rec.to_dict()

    assert dict(affiliation_dict, **updated_affiliation) == affiliation_dict

    # not-ideal cleanup
    affiliation_rec._record.delete(force=True)
