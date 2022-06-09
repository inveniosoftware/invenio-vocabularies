# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Awards datastreams tests."""

from copy import deepcopy

import pytest
from invenio_access.permissions import system_identity

from invenio_vocabularies.contrib.awards.api import Award
from invenio_vocabularies.contrib.awards.datastreams import (
    AwardsServiceWriter,
    OpenAIREProjectTransformer,
)
from invenio_vocabularies.datastreams import StreamEntry
from invenio_vocabularies.datastreams.errors import WriterError


@pytest.fixture(scope="function")
def dict_award_entry():
    return StreamEntry(
        {
            "acronym": "TA",
            "code": "0751743",
            "enddate": "2010-09-30",
            "funding": [
                {
                    "funding_stream": {
                        "description": "Directorate for Geosciences - Division of "
                        "Ocean Sciences",
                        "id": "NSF::GEO/OAD::GEO/OCE",
                    },
                    "jurisdiction": "US",
                    "name": "National Science Foundation",
                    "shortName": "NSF",
                }
            ],
            "h2020programme": [],
            "id": "40|nsf_________::3eb1b4f6d6e251a19f9fdeed2aab88d8",
            "openaccessmandatefordataset": False,
            "openaccessmandateforpublications": False,
            "startdate": "2008-04-01",
            "subject": ["Oceanography"],
            "title": "Test title",
            "websiteurl": "https://test.com",
        }
    )


@pytest.fixture(scope="function")
def dict_award_entry_ec():
    """Full award data."""
    return StreamEntry(
        {
            "acronym": "TS",
            "code": "129123",
            "enddate": "2025-12-31",
            "funding": [
                {
                    "funding_stream": {
                        "description": "Test stream",
                        "id": "TST::test::test",
                    },
                    "jurisdiction": "GR",
                    "name": "Test Name",
                    "shortName": "TST",
                }
            ],
            "h2020programme": [],
            "id": "40|corda__h2020::000000000000000000",
            "openaccessmandatefordataset": False,
            "openaccessmandateforpublications": False,
            "startdate": "2008-04-01",
            "subject": ["Oceanography"],
            "title": "Test title",
            "websiteurl": "https://test.com",
        }
    )


@pytest.fixture(scope="function")
def expected_from_award_json():
    return {
        "id": "021nxhr62::0751743",
        "identifiers": [{"identifier": "https://test.com", "scheme": "url"}],
        "number": "0751743",
        "title": {"en": "Test title"},
        "funder": {"id": "021nxhr62"},
        "acronym": "TA",
    }


@pytest.fixture(scope="function")
def expected_from_award_json_ec():
    return {
        "id": "00k4n6c32::129123",
        "identifiers": [
            {"identifier": "https://cordis.europa.eu/projects/129123", "scheme": "url"}
        ],
        "number": "129123",
        "title": {"en": "Test title"},
        "funder": {"id": "00k4n6c32"},
        "acronym": "TS",
    }


def test_awards_transformer(app, dict_award_entry, expected_from_award_json):
    transformer = OpenAIREProjectTransformer()
    assert expected_from_award_json == transformer.apply(dict_award_entry).entry


def test_awards_service_writer_create(
    app, es_clear, example_funder_ec, award_full_data
):
    awards_writer = AwardsServiceWriter("awards", system_identity)
    award_rec = awards_writer.write(StreamEntry(award_full_data))
    award_dict = award_rec.entry.to_dict()

    award_full_data["funder"]["name"] = example_funder_ec["name"]
    assert dict(award_dict, **award_full_data) == award_dict

    # not-ideal cleanup
    award_rec.entry._record.delete(force=True)


def test_awards_funder_id_not_exist(
    app,
    es_clear,
    example_funder,
    example_funder_ec,
    award_full_data_invalid_id,
):
    awards_writer = AwardsServiceWriter("awards", system_identity)
    with pytest.raises(WriterError) as err:
        awards_writer.write(StreamEntry(award_full_data_invalid_id))
    expected_error = [
        {
            "InvalidRelationValue": "Invalid value {funder_id}.".format(
                funder_id=award_full_data_invalid_id.get("funder").get("id")
            )
        }
    ]

    assert expected_error in err.value.args


def test_awards_funder_id_not_exist_no_funders(
    app, es_clear, award_full_data_invalid_id
):
    awards_writer = AwardsServiceWriter("awards", system_identity)
    with pytest.raises(WriterError) as err:
        awards_writer.write(StreamEntry(award_full_data_invalid_id))
    expected_error = [
        {
            "InvalidRelationValue": "Invalid value {funder_id}.".format(
                funder_id=award_full_data_invalid_id.get("funder").get("id")
            )
        }
    ]

    assert expected_error in err.value.args


def test_awards_transformer_ec_functionality(
    app,
    es_clear,
    dict_award_entry,
    dict_award_entry_ec,
    expected_from_award_json,
    expected_from_award_json_ec,
):
    transformer = OpenAIREProjectTransformer()
    assert expected_from_award_json == transformer.apply(dict_award_entry).entry
    assert expected_from_award_json_ec == transformer.apply(dict_award_entry_ec).entry


def test_awards_service_writer_duplicate(
    app, es_clear, example_funder_ec, award_full_data
):
    writer = AwardsServiceWriter("awards", system_identity)
    award_rec = writer.write(stream_entry=StreamEntry(award_full_data))
    Award.index.refresh()  # refresh index to make changes live
    with pytest.raises(WriterError) as err:
        writer.write(stream_entry=StreamEntry(award_full_data))

    expected_error = [f"Vocabulary entry already exists: {award_full_data}"]
    assert expected_error in err.value.args

    # not-ideal cleanup
    award_rec.entry._record.delete(force=True)


def test_awards_service_writer_update_existing(
    app, es_clear, example_funder_ec, award_full_data, service
):
    # create vocabulary
    writer = AwardsServiceWriter("awards", system_identity, update=True)
    orig_award_rec = writer.write(stream_entry=StreamEntry(award_full_data))
    Award.index.refresh()  # refresh index to make changes live
    # update vocabulary
    updated_award = deepcopy(award_full_data)
    updated_award["title"] = {"en": "New Test title"}
    # check changes vocabulary
    _ = writer.write(stream_entry=StreamEntry(updated_award))
    award_rec = service.read(system_identity, orig_award_rec.entry.id)
    award_dict = award_rec.to_dict()

    updated_award["funder"]["name"] = example_funder_ec["name"]
    # needed while the writer resolves from ES
    assert _.entry.id == orig_award_rec.entry.id
    assert dict(award_dict, **updated_award) == award_dict

    # not-ideal cleanup
    award_rec._record.delete(force=True)


def test_awards_service_writer_update_non_existing(
    app, es_clear, example_funder_ec, award_full_data, service
):
    # vocabulary item not created, call update directly
    updated_award = deepcopy(award_full_data)
    updated_award["title"] = {"en": "New Test title"}
    # check changes vocabulary
    writer = AwardsServiceWriter("awards", system_identity, update=True)
    award_rec = writer.write(stream_entry=StreamEntry(updated_award))
    award_rec = service.read(system_identity, award_rec.entry.id)
    award_dict = award_rec.to_dict()

    updated_award["funder"]["name"] = example_funder_ec["name"]
    assert dict(award_dict, **updated_award) == award_dict

    # not-ideal cleanup
    award_rec._record.delete(force=True)
