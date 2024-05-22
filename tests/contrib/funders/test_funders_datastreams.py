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
from invenio_vocabularies.contrib.funders.datastreams import (
    FundersServiceWriter,
    RORTransformer,
)
from invenio_vocabularies.datastreams import StreamEntry
from invenio_vocabularies.datastreams.errors import WriterError


@pytest.fixture(scope="module")
def dict_ror_entry():
    return StreamEntry(
        {
            "locations": [
                {
                    "geonames_id": 5381396,
                    "geonames_details": {
                        "country_code": "US",
                        "country_name": "United States",
                        "lat": 34.14778,
                        "lng": -118.14452,
                        "name": "Pasadena",
                    },
                }
            ],
            "established": 1891,
            "external_ids": [
                {
                    "type": "fundref",
                    "all": ["100006961", "100009676"],
                    "preferred": "100006961",
                },
                {
                    "type": "grid",
                    "all": ["grid.20861.3d"],
                    "preferred": "grid.20861.3d",
                },
                {"type": "isni", "all": ["0000 0001 0706 8890"], "preferred": None},
                {"type": "wikidata", "all": ["Q161562"], "preferred": None},
            ],
            "id": "https://ror.org/05dxps055",
            "domains": [],
            "links": [
                {"type": "website", "value": "http://www.caltech.edu/"},
                {
                    "type": "wikipedia",
                    "value": "http://en.wikipedia.org/wiki/California_Institute_of_Technology",
                },
            ],
            "names": [
                {"value": "CIT", "types": ["acronym"], "lang": None},
                {
                    "value": "California Institute of Technology",
                    "types": ["ror_display", "label"],
                    "lang": "en",
                },
                {"value": "Caltech", "types": ["alias"], "lang": None},
                {
                    "value": "Instituto de Tecnología de California",
                    "types": ["label"],
                    "lang": "es",
                },
            ],
            "relationships": [
                {
                    "label": "Caltech Submillimeter Observatory",
                    "type": "child",
                    "id": "https://ror.org/01e6j9276",
                },
                {
                    "label": "Infrared Processing and Analysis Center",
                    "type": "child",
                    "id": "https://ror.org/05q79g396",
                },
                {
                    "label": "Joint Center for Artificial Photosynthesis",
                    "type": "child",
                    "id": "https://ror.org/05jtgpc57",
                },
                {
                    "label": "Keck Institute for Space Studies",
                    "type": "child",
                    "id": "https://ror.org/05xkke381",
                },
                {
                    "label": "Jet Propulsion Laboratory",
                    "type": "child",
                    "id": "https://ror.org/027k65916",
                },
                {
                    "label": "Institute for Collaborative Biotechnologies",
                    "type": "child",
                    "id": "https://ror.org/04kz4p343",
                },
                {
                    "label": "Resnick Sustainability Institute",
                    "type": "child",
                    "id": "https://ror.org/04bxjes65",
                },
            ],
            "status": "active",
            "types": ["education", "funder"],
            "admin": {
                "created": {"date": "2018-11-14", "schema_version": "1.0"},
                "last_modified": {"date": "2024-05-13", "schema_version": "2.0"},
            },
        },
    )


@pytest.fixture(scope="module")
def expected_from_ror_json():
    return {
        "id": "05dxps055",
        "name": "California Institute of Technology",
        "title": {
            "en": "California Institute of Technology",
            "es": "Instituto de Tecnología de California",
        },
        "acronym": "CIT",
        "aliases": ["Caltech"],
        "country": "US",
        "country_name": "United States",
        "location_name": "Pasadena",
        "status": "active",
        "identifiers": [
            {"scheme": "ror", "identifier": "05dxps055"},
            {"scheme": "doi", "identifier": "10.13039/100006961"},
            {"scheme": "grid", "identifier": "grid.20861.3d"},
            {"scheme": "isni", "identifier": "0000 0001 0706 8890"},
        ],
        "types": ["education", "funder"],
    }


def test_ror_transformer(app, dict_ror_entry, expected_from_ror_json):
    transformer = RORTransformer()
    assert expected_from_ror_json == transformer.apply(dict_ror_entry).entry


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
