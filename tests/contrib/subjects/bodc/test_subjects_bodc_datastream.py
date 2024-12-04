# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

import io

import pytest
from rdflib import Graph

from invenio_vocabularies.contrib.subjects.bodc.datastreams import (
    BODCPUVSubjectsTransformer,
)
from invenio_vocabularies.datastreams.datastreams import StreamEntry
from invenio_vocabularies.datastreams.errors import TransformerError
from invenio_vocabularies.datastreams.readers import RDFReader

VALID_XML_DATA = bytes(
    """<?xml version="1.0" encoding="UTF-8"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:skos="http://www.w3.org/2004/02/skos/core#" xmlns:dc="http://purl.org/dc/terms/" xmlns:dce="http://purl.org/dc/elements/1.1/" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:grg="http://www.isotc211.org/schemas/grg/" xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:void="http://rdfs.org/ns/void#" xmlns:pav="http://purl.org/pav/" xmlns:prov="https://www.w3.org/ns/prov#" xmlns:reg="http://purl.org/linked-data/registry#" xmlns:cpm="http://purl.org/voc/cpm#" xmlns:qudt="https://qudt.org/2.1/schema/qudt#" xmlns:semapv="http://w3id.org/semapv/vocab/" xmlns:iop="https://w3id.org/iadopt/ont#" xmlns:sssom="https://w3id.org/sssom/schema/" xmlns:puv="https://w3id.org/env/puv#">
    <skos:Collection rdf:about="http://vocab.nerc.ac.uk/collection/P01/current/">
        <skos:prefLabel>BODC Parameter Usage Vocabulary</skos:prefLabel>
        <dc:title>BODC Parameter Usage Vocabulary</dc:title>
        <skos:altLabel>BODC PUV</skos:altLabel>
        <dc:alternative>BODC PUV</dc:alternative>
        <dc:description>Terms built using the BODC parameter semantic model designed to describe individual measured phenomena. May be used to mark up sets of data such as a NetCDF array or spreadsheet column. Units must be specified when using a P01 code. The P06 unit that is linked to individual P01 in the NVS is the one used in BODC's systems but external users can use any appropriate units.</dc:description>
        <dc:license rdf:resource="https://creativecommons.org/licenses/by/4.0/"/>
        <skos:member>
            <skos:Concept xml:base="http://vocab.nerc.ac.uk/collection/P01/current/SAGEMSFM/" rdf:about="http://vocab.nerc.ac.uk/collection/P01/current/SAGEMSFM/">
                <dc:identifier>SDN:P01::SAGEMSFM</dc:identifier>
                <dce:identifier>SDN:P01::SAGEMSFM</dce:identifier>
                <dc:date>2008-10-16 16:27:06.0</dc:date>
                <skos:notation>SDN:P01::SAGEMSFM</skos:notation>
                <skos:prefLabel xml:lang="en">14C age of Foraminiferida (ITIS: 44030: WoRMS 22528) [Subcomponent: tests] in sediment by picking and accelerator mass spectrometry</skos:prefLabel>
                <skos:altLabel>AMSSedAge</skos:altLabel>
                <skos:definition xml:lang="en">Accelerated mass spectrometry on picked tests</skos:definition>
                <owl:versionInfo>1</owl:versionInfo>
                <pav:hasCurrentVersion rdf:resource="http://vocab.nerc.ac.uk/collection/P01/current/SAGEMSFM/1/"/>
                <pav:version>1</pav:version>
                <pav:authoredOn>2008-10-16 16:27:06.0</pav:authoredOn>
                <skos:note xml:lang="en">accepted</skos:note>
                <owl:deprecated>false</owl:deprecated>
                <iop:hasMatrix rdf:resource="http://vocab.nerc.ac.uk/collection/S21/current/S21S022/"/>
                <skos:related rdf:resource="http://vocab.nerc.ac.uk/collection/P06/current/UYBP/"/>
                <skos:broader rdf:resource="http://vocab.nerc.ac.uk/collection/S25/current/BE002325/"/>
                <skos:broader rdf:resource="http://vocab.nerc.ac.uk/collection/S26/current/MAT00136/"/>
                <void:inDataset rdf:resource="http://vocab.nerc.ac.uk/.well-known/void"/>
            </skos:Concept>
        </skos:member>    
    </skos:Collection>
</rdf:RDF>""",
    encoding="utf-8",
)

INVALID_XML_DATA = bytes(
    """<?xml version="1.0" encoding="UTF-8"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:skos="http://www.w3.org/2004/02/skos/core#">
    <skos:Collection rdf:about="http://vocab.nerc.ac.uk/collection/P01/current/">
        <skos:member>
            <skos:Concept rdf:about="http://vocab.nerc.ac.uk/collection/P01/current/SAGEMSFM/">
                <skos:prefLabel>Invalid Data</skos:prefLabel>
                <!-- No skos:notation present -->
            </skos:Concept>
        </skos:member>
    </skos:Collection>
</rdf:RDF>""",
    encoding="utf-8",
)


@pytest.fixture(scope="module")
def expected_from_rdf():
    return [
        {
            "id": "SDN:P01::SAGEMSFM",
            "scheme": "BODC-PUV",
            "subject": "AMSSedAge",
            "title": {
                "en": "14c age of foraminiferida (itis: 44030: worms 22528) [subcomponent: tests] in sediment by picking and accelerator mass spectrometry",
            },
            "props": {"definition": "Accelerated mass spectrometry on picked tests"},
            "identifiers": [
                {
                    "scheme": "url",
                    "identifier": "http://vocab.nerc.ac.uk/collection/P01/current/SAGEMSFM/",
                }
            ],
        }
    ]


def parse_rdf_data(rdf_data):
    """Parse RDF data and return a list of stream entries."""
    reader = RDFReader()
    rdf_graph = Graph()
    rdf_graph.parse(io.BytesIO(rdf_data), format="xml")
    return list(reader._iter(rdf_graph))[0]


def test_bodc_puv_transformer_pref_label(expected_from_rdf):
    stream_entry = parse_rdf_data(VALID_XML_DATA)
    assert len(stream_entry) > 0
    transformer = BODCPUVSubjectsTransformer()
    result = []
    entry = transformer.apply(StreamEntry(stream_entry)).entry
    result.append(entry)
    assert expected_from_rdf == result


def test_bodc_puv_transformer_missing_id():
    stream_entry = parse_rdf_data(INVALID_XML_DATA)
    assert len(stream_entry) > 0

    transformer = BODCPUVSubjectsTransformer()

    with pytest.raises(TransformerError) as err:
        transformer.apply(StreamEntry(stream_entry))

    expected_error = f"No id found for: {stream_entry['subject']}"

    assert expected_error in err.value.args
