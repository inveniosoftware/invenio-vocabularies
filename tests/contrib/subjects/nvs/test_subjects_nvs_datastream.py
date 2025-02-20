# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

import io

import pytest
from rdflib import Graph

from invenio_vocabularies.contrib.subjects.nvs.datastreams import NVSSubjectsTransformer
from invenio_vocabularies.datastreams.datastreams import StreamEntry
from invenio_vocabularies.datastreams.errors import TransformerError
from invenio_vocabularies.datastreams.readers import RDFReader

VALID_XML_DATA = bytes(
    """<?xml version="1.0" encoding="UTF-8"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:skos="http://www.w3.org/2004/02/skos/core#" xmlns:dc="http://purl.org/dc/terms/" xmlns:dce="http://purl.org/dc/elements/1.1/" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:grg="http://www.isotc211.org/schemas/grg/" xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:void="http://rdfs.org/ns/void#" xmlns:pav="http://purl.org/pav/" xmlns:prov="https://www.w3.org/ns/prov#" xmlns:reg="http://purl.org/linked-data/registry#" xmlns:cpm="http://purl.org/voc/cpm#" xmlns:qudt="https://qudt.org/2.1/schema/qudt#" xmlns:semapv="http://w3id.org/semapv/vocab/" xmlns:iop="https://w3id.org/iadopt/ont#" xmlns:sssom="https://w3id.org/sssom/schema/" xmlns:puv="https://w3id.org/env/puv#">
  <rdf:Description rdf:about="http://vocab.nerc.ac.uk/collection/P02/current/QDMD/">
    <pav:authoredOn>2008-08-15 10:07:03.0</pav:authoredOn>
    <pav:hasCurrentVersion rdf:resource="http://vocab.nerc.ac.uk/collection/P02/current/QDMD/1/"/>
    <dce:identifier>SDN:P02::QDMD</dce:identifier>
    <pav:version>1</pav:version>
    <skos:broader rdf:resource="http://vocab.nerc.ac.uk/collection/C47/current/IN6_1_2/"/>
    <skos:broader rdf:resource="http://vocab.nerc.ac.uk/collection/P22/current/19/"/>
    <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/>
    <skos:definition xml:lang="en">Parameters quantifying the amount of liquids (e.g. ship's ballast) or solids (e.g. dredge spoil) deposited into the water column as a result of man's activities</skos:definition>
    <void:inDataset rdf:resource="http://vocab.nerc.ac.uk/.well-known/void"/>
    <owl:deprecated>false</owl:deprecated>
    <skos:note xml:lang="en">accepted</skos:note>
    <dc:identifier>SDN:P02::QDMD</dc:identifier>
    <skos:prefLabel xml:lang="en">Quantity of material dumped</skos:prefLabel>
    <owl:versionInfo>1</owl:versionInfo>
    <dc:date>2008-08-15 10:07:03.0</dc:date>
    <skos:altLabel>Amount_dumped</skos:altLabel>
    <skos:inScheme rdf:resource="http://vocab.nerc.ac.uk/scheme/EDMED_DCAT_THEMES/current/"/>
    <skos:notation>SDN:P02::QDMD</skos:notation>
    <skos:broader rdf:resource="http://vocab.nerc.ac.uk/collection/D01/current/D0100001/"/>
    <skos:broader rdf:resource="http://vocab.nerc.ac.uk/collection/L19/current/005/"/>
    <skos:broader rdf:resource="http://vocab.nerc.ac.uk/collection/P03/current/H001/"/>
    <skos:broader rdf:resource="http://vocab.nerc.ac.uk/collection/P05/current/007/"/>
  </rdf:Description>
</rdf:RDF>""",
    encoding="utf-8",
)

INVALID_XML_DATA = bytes(
    """<?xml version="1.0" encoding="UTF-8"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:skos="http://www.w3.org/2004/02/skos/core#">
    <skos:Collection rdf:about="http://vocab.nerc.ac.uk/collection/P02/current/">
        <skos:member>
            <skos:Concept rdf:about="http://vocab.nerc.ac.uk/collection/P02/current/QDMD/">
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
            "id": "SDN:P02::QDMD",
            "scheme": "NVS-P02",
            "subject": "Quantity of material dumped",
            "title": {
                "en": "Quantity of material dumped",
            },
            "props": {
                "definition": "Parameters quantifying the amount of liquids (e.g. ship's ballast) or solids (e.g. dredge spoil) deposited into the water column as a result of man's activities"
            },
            "identifiers": [
                {
                    "scheme": "url",
                    "identifier": "http://vocab.nerc.ac.uk/collection/P02/current/QDMD/",
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


def test_nvs_transformer_pref_label(expected_from_rdf):
    stream_entry = parse_rdf_data(VALID_XML_DATA)
    assert len(stream_entry) > 0
    transformer = NVSSubjectsTransformer()
    result = []
    entry = transformer.apply(StreamEntry(stream_entry)).entry
    result.append(entry)
    assert expected_from_rdf == result


def test_nvs_transformer_missing_id():
    stream_entry = parse_rdf_data(INVALID_XML_DATA)
    assert len(stream_entry) > 0

    transformer = NVSSubjectsTransformer()

    with pytest.raises(TransformerError) as err:
        transformer.apply(StreamEntry(stream_entry))

    expected_error = f"No id found for: {stream_entry['subject']}"

    assert expected_error in err.value.args
