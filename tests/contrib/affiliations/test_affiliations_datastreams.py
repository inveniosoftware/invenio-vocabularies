# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
# Copyright (C) 2024 California Institute of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Affiliations datastreams tests."""

from copy import deepcopy
from unittest.mock import patch

import pytest
from invenio_access.permissions import system_identity

from invenio_vocabularies.contrib.affiliations.api import Affiliation
from invenio_vocabularies.contrib.affiliations.config import affiliation_schemes
from invenio_vocabularies.contrib.affiliations.datastreams import (
    AffiliationsServiceWriter,
    EDMOOrganizationTransformer,
    OpenAIREAffiliationsServiceWriter,
    OpenAIREOrganizationTransformer,
)
from invenio_vocabularies.contrib.common.ror.datastreams import RORTransformer
from invenio_vocabularies.datastreams import StreamEntry
from invenio_vocabularies.datastreams.errors import TransformerError, WriterError
from invenio_vocabularies.datastreams.readers import SPARQLReader

EDMO_SPARQL_JSON_RESPONSE_CONTENT = {
    "head": {
        "vars": ["org", "name", "altName", "countryName", "locality", "deprecated"]
    },
    "results": {
        "bindings": [
            {
                "org": {"type": "uri", "value": "https://edmo.seadatanet.org/report/1"},
                "name": {"type": "literal", "value": "Org One Name"},
                "altName": {"type": "literal", "value": "ONE"},
                "countryName": {"type": "literal", "value": "United Kingdom"},
                "locality": {"type": "literal", "value": "Liverpool"},
                "deprecated": {
                    "type": "literal",
                    "datatype": "http://www.w3.org/2001/XMLSchema#boolean",
                    "value": "false",
                },
            },
            {
                "org": {"type": "uri", "value": "https://edmo.seadatanet.org/report/2"},
                "name": {"type": "literal", "value": "Org Two Name"},
                "altName": {"type": "literal", "value": "TWO"},
                "countryName": {"type": "literal", "value": "Germany"},
                "locality": {"type": "literal", "value": "Hamburg"},
                "deprecated": {
                    "type": "literal",
                    "datatype": "http://www.w3.org/2001/XMLSchema#boolean",
                    "value": "false",
                },
            },
        ]
    },
}


class MockSPARQLWrapperQuery:
    def __init__(self, sparql_json_response_content):
        self.sparql_json_response_content = sparql_json_response_content

    def convert(self):
        return self.sparql_json_response_content


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
            {"scheme": "grid", "identifier": "grid.20861.3d"},
            {"scheme": "isni", "identifier": "0000 0001 0706 8890"},
        ],
        "types": ["education", "funder"],
    }


def test_ror_transformer(app, dict_ror_entry, expected_from_ror_json):
    """Test RORTransformer to ensure it transforms ROR entries correctly."""
    transformer = RORTransformer(vocab_schemes=affiliation_schemes)
    assert expected_from_ror_json == transformer.apply(dict_ror_entry).entry


def test_affiliations_service_writer_create(app, search_clear, affiliation_full_data):
    """Test AffiliationsServiceWriter for creating a new affiliation."""
    writer = AffiliationsServiceWriter()
    affiliation_rec = writer.write(StreamEntry(affiliation_full_data))
    affiliation_dict = affiliation_rec.entry.to_dict()
    assert dict(affiliation_dict, **affiliation_full_data) == affiliation_dict

    # not-ideal cleanup
    affiliation_rec.entry._record.delete(force=True)


def test_affiliations_service_writer_duplicate(
    app, search_clear, affiliation_full_data
):
    """Test AffiliationsServiceWriter for handling duplicate entries."""
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
    """Test updating an existing affiliation using AffiliationsServiceWriter."""
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
    """Test creating a new affiliation when updating a non-existing entry."""
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


@pytest.fixture()
def dict_openaire_organization_entry():
    """An example entry from OpenAIRE organization Data Dump."""
    return StreamEntry(
        {
            "alternativeNames": [
                "European Organization for Nuclear Research",
                "Organisation européenne pour la recherche nucléaire",
                "CERN",
            ],
            "country": {"code": "CH", "label": "Switzerland"},
            "id": "openorgs____::47efb6602225236c0b207761a8b3a21c",
            "legalName": "European Organization for Nuclear Research",
            "legalShortName": "CERN",
            "pid": [
                {"scheme": "mag_id", "value": "67311998"},
                {"scheme": "ISNI", "value": "000000012156142X"},
                {"scheme": "Wikidata", "value": "Q42944"},
                {"scheme": "ROR", "value": "https://ror.org/01ggx4157"},
                {"scheme": "PIC", "value": "999988133"},
                {"scheme": "OrgReg", "value": "INT1011"},
                {"scheme": "ISNI", "value": "000000012156142X"},
                {"scheme": "FundRef", "value": "100012470"},
                {"scheme": "GRID", "value": "grid.9132.9"},
                {"scheme": "OrgRef", "value": "37351"},
            ],
            "websiteUrl": "http://home.web.cern.ch/",
        }
    )


@pytest.fixture(scope="module")
def expected_from_openaire_json():
    return {
        "id": "01ggx4157",
        "identifiers": [{"identifier": "999988133", "scheme": "pic"}],
    }


def test_openaire_organization_transformer(
    app, dict_openaire_organization_entry, expected_from_openaire_json
):
    """Test OpenAIREOrganizationTransformer for transforming OpenAIRE entries."""
    transformer = OpenAIREOrganizationTransformer()
    assert (
        expected_from_openaire_json
        == transformer.apply(dict_openaire_organization_entry).entry
    )


def test_openaire_affiliations_service_writer(
    app,
    search_clear,
    affiliation_full_data,
    openaire_affiliation_full_data,
    service,
):
    """Test writing and updating an OpenAIRE affiliation entry."""
    # create vocabulary with original service writer
    orig_writer = AffiliationsServiceWriter()

    orig_affiliation_rec = orig_writer.write(StreamEntry(affiliation_full_data))

    orig_affiliation_dict = orig_affiliation_rec.entry.to_dict()
    Affiliation.index.refresh()  # refresh index to make changes live

    # update vocabulary and check changes vocabulary with OpenAIRE service writer
    writer = OpenAIREAffiliationsServiceWriter()

    _ = writer.write(StreamEntry(openaire_affiliation_full_data))
    Affiliation.index.refresh()  # refresh index to make changes live
    affiliation_rec = service.read(system_identity, orig_affiliation_rec.entry.id)
    affiliation_dict = affiliation_rec.to_dict()

    assert _.entry.id == orig_affiliation_rec.entry.id

    # updating fields changing from one update to the other
    orig_affiliation_dict["revision_id"] = affiliation_dict["revision_id"]
    orig_affiliation_dict["updated"] = affiliation_dict["updated"]
    # Adding the extra identifier coming from OpenAIRE
    orig_affiliation_dict["identifiers"].extend(
        openaire_affiliation_full_data["identifiers"]
    )

    assert dict(orig_affiliation_dict) == affiliation_dict

    # not-ideal cleanup
    affiliation_rec._record.delete(force=True)


def test_openaire_affiliations_transformer_non_openorgs(
    app, dict_openaire_organization_entry
):
    """Test error handling for non-OpenOrgs ID in OpenAIRE transformer."""
    transformer = OpenAIREOrganizationTransformer()

    updated_organization_entry = deepcopy(dict_openaire_organization_entry.entry)
    updated_organization_entry["id"] = "pending_org_::627931d047132a4e20dbc4a882eb9a35"

    with pytest.raises(TransformerError) as err:
        transformer.apply(StreamEntry(updated_organization_entry))

    expected_error = [
        f"Not valid OpenAIRE OpenOrgs id for: {updated_organization_entry}"
    ]
    assert expected_error in err.value.args


def test_openaire_affiliations_transformer_no_id(app, dict_openaire_organization_entry):
    """Test error handling when missing ID in OpenAIRE transformer."""
    transformer = OpenAIREOrganizationTransformer()

    updated_organization_entry = deepcopy(dict_openaire_organization_entry.entry)
    updated_organization_entry.pop("id", None)

    with pytest.raises(TransformerError) as err:
        transformer.apply(StreamEntry(updated_organization_entry))

    expected_error = [f"No id for: {updated_organization_entry}"]
    assert expected_error in err.value.args


def test_openaire_affiliations_transformer_no_alternative_identifiers(
    app, dict_openaire_organization_entry
):
    """Test error handling when missing alternative identifiers in OpenAIRE transformer."""
    transformer = OpenAIREOrganizationTransformer()

    updated_organization_entry = deepcopy(dict_openaire_organization_entry.entry)
    updated_organization_entry.pop("pid", None)

    with pytest.raises(TransformerError) as err:
        transformer.apply(StreamEntry(updated_organization_entry))

    expected_error = [f"No alternative identifiers for: {updated_organization_entry}"]
    assert expected_error in err.value.args


@patch(
    "SPARQLWrapper.SPARQLWrapper.query",
    side_effect=lambda: MockSPARQLWrapperQuery(EDMO_SPARQL_JSON_RESPONSE_CONTENT),
)
def test_edmo_organization_http_reader(_):
    reader = SPARQLReader(
        origin="http://example.com/sparql/sparql",
        query="""
                        SELECT ?org ?name ?altName ?countryName ?locality ?deprecated WHERE {
                        ?org a <http://www.w3.org/ns/org#Organization> .
                        ?org <http://www.w3.org/ns/org#name> ?name .
                        OPTIONAL { ?org <http://www.w3.org/2004/02/skos/core#altName> ?altName } .
                        OPTIONAL { ?org <http://www.w3.org/2006/vcard/ns#country-name> ?countryName } .
                        OPTIONAL { ?org <http://www.w3.org/2006/vcard/ns#locality> ?locality } .
                        OPTIONAL { ?org <http://www.w3.org/2002/07/owl#deprecated> ?deprecated } .
                        FILTER (!?deprecated)}""",
    )
    results = []
    for entry in reader.read():
        results.append(entry)
        assert list(entry.keys()) == [
            "org",
            "name",
            "altName",
            "countryName",
            "locality",
            "deprecated",
        ]
    assert len(results) == 2


@pytest.fixture()
def expected_from_edmo_json():
    return {
        "id": "edmo:1",
        "identifiers": [{"identifier": "edmo:1", "scheme": "edmo"}],
        "name": "Org One Name",
        "title": {"en": "Org One Name"},
        "acronym": "ONE",
        "country_name": "United Kingdom",
        "country": "GB",
        "location_name": "Liverpool",
    }


@pytest.fixture()
def dict_edmo_organization_entry():
    """An example entry from EDMO organization Data Dump."""
    return StreamEntry(
        {
            "org": {"type": "uri", "value": "https://edmo.seadatanet.org/report/1"},
            "name": {"type": "literal", "value": "Org One Name"},
            "altName": {"type": "literal", "value": "ONE"},
            "countryName": {"type": "literal", "value": "United Kingdom"},
            "locality": {"type": "literal", "value": "Liverpool"},
            "deprecated": {
                "type": "literal",
                "datatype": "http://www.w3.org/2001/XMLSchema#boolean",
                "value": "false",
            },
        }
    )


@pytest.fixture()
def test_edmo_organization_transformer(
    dict_edmo_organization_entry, expected_from_edmo_json
):
    transformer = EDMOOrganizationTransformer()
    result = transformer.apply(dict_edmo_organization_entry)
    assert expected_from_edmo_json == result.entry
