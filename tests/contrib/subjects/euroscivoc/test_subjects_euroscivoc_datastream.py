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

from invenio_vocabularies.contrib.subjects.euroscivoc.datastreams import (
    EuroSciVocSubjectsTransformer,
)
from invenio_vocabularies.datastreams.datastreams import StreamEntry
from invenio_vocabularies.datastreams.readers import RDFReader

XML_DATA_PREF_LABEL = bytes(
    """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:skos="http://www.w3.org/2004/02/skos/core#" xmlns:ns5="http://publications.europa.eu/ontology/euvoc#" xmlns:ns6="http://www.w3.org/2008/05/skos-xl#" xmlns:dc="http://purl.org/dc/elements/1.1/">
    <rdf:Description rdf:about="http://data.europa.eu/8mn/euroscivoc/87ff3577-527a-4a40-9c76-2f9d3075e2ba">
        <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/>
        <dcterms:created rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2019-12-02</dcterms:created>
        <dcterms:modified rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2019-12-02</dcterms:modified>
        <owl:versionInfo>1.1.0</owl:versionInfo>
        <skos:inScheme rdf:resource="http://data.europa.eu/8mn/euroscivoc/40c0f173-baa3-48a3-9fe6-d6e8fb366a00"/>
        <skos:prefLabel xml:lang="it">radio satellitare</skos:prefLabel>
        <skos:prefLabel xml:lang="pl">radio satelitarne</skos:prefLabel>
        <skos:prefLabel xml:lang="fr">radio satellite</skos:prefLabel>
        <skos:prefLabel xml:lang="es">radio por satélite</skos:prefLabel>
        <skos:prefLabel xml:lang="de">Satellitenfunk</skos:prefLabel>
        <skos:prefLabel xml:lang="en">satellite radio</skos:prefLabel>
        <ns5:startDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2019-12-02</ns5:startDate>
        <skos:notation>87ff3577-527a-4a40-9c76-2f9d3075e2ba</skos:notation>
        <skos:notation>1717</skos:notation>
        <ns5:status rdf:resource="http://publications.europa.eu/resource/authority/concept-status/CURRENT"/>
        <ns5:xlNotation rdf:resource="http://data.europa.eu/8mn/euroscivoc/7f282340-9125-4b0d-aceb-23389311e306"/>
        <ns5:xlNotation rdf:resource="http://data.europa.eu/8mn/euroscivoc/notation_6014c8c4f809ee00ced00312669d98ad"/>
        <skos:altLabel xml:lang="en">broadcastingsatellite service</skos:altLabel>
        <skos:altLabel xml:lang="en">satellite radio system</skos:altLabel>
        <skos:broader rdf:resource="http://data.europa.eu/8mn/euroscivoc/d913bd42-e79c-46a7-8714-14f2a6a0d82f"/>
        <dc:identifier>87ff3577-527a-4a40-9c76-2f9d3075e2ba</dc:identifier>
        <owl:deprecated rdf:datatype="http://www.w3.org/2001/XMLSchema#boolean">false</owl:deprecated>
        </rdf:Description>
        <rdf:Description rdf:about="http://data.europa.eu/8mn/euroscivoc/d913bd42-e79c-46a7-8714-14f2a6a0d82f">
        <skos:narrower rdf:resource="http://data.europa.eu/8mn/euroscivoc/87ff3577-527a-4a40-9c76-2f9d3075e2ba"/>
    </rdf:Description>
     <rdf:Description rdf:about="http://data.europa.eu/8mn/euroscivoc/87ff3577-527a-4a40-9c76-2f9d3075e2ba">
            <skos:broader rdf:resource="http://data.europa.eu/8mn/euroscivoc/d913bd42-e79c-46a7-8714-14f2a6a0d82f"/>
            </rdf:Description>
            <rdf:Description rdf:about="http://data.europa.eu/8mn/euroscivoc/8d83b645-355f-4cf1-abf3-ce4cd3172c34">
            <skos:broader rdf:resource="http://data.europa.eu/8mn/euroscivoc/d913bd42-e79c-46a7-8714-14f2a6a0d82f"/>
            </rdf:Description>
            <rdf:Description rdf:about="http://data.europa.eu/8mn/euroscivoc/d913bd42-e79c-46a7-8714-14f2a6a0d82f">
            <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/>
            <dcterms:created rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2019-12-02</dcterms:created>
            <dcterms:modified rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2023-03-10</dcterms:modified>
            <owl:versionInfo>1.3.4</owl:versionInfo>
            <skos:inScheme rdf:resource="http://data.europa.eu/8mn/euroscivoc/40c0f173-baa3-48a3-9fe6-d6e8fb366a00"/>
            <ns5:startDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2019-12-02</ns5:startDate>
            <skos:notation>1225</skos:notation>
            <skos:notation>d913bd42-e79c-46a7-8714-14f2a6a0d82f</skos:notation>
            <ns5:status rdf:resource="http://publications.europa.eu/resource/authority/concept-status/CURRENT"/>
            <ns5:xlNotation rdf:resource="http://data.europa.eu/8mn/euroscivoc/notation_1391bd2069b8dde8f6394b6a3b4241cb"/>
            <ns5:xlNotation rdf:resource="http://data.europa.eu/8mn/euroscivoc/1faa45c8-4f46-45d6-9d6f-447a2626125d"/>
            <skos:altLabel xml:lang="en">radio channel</skos:altLabel>
            <skos:altLabel xml:lang="en">wireless</skos:altLabel>
            <skos:broader rdf:resource="http://data.europa.eu/8mn/euroscivoc/1198b23a-f82f-4189-8778-d9a742430a0f"/>
            <dc:identifier>d913bd42-e79c-46a7-8714-14f2a6a0d82f</dc:identifier>
            <owl:deprecated rdf:datatype="http://www.w3.org/2001/XMLSchema#boolean">false</owl:deprecated>
        </rdf:Description>
</rdf:RDF>""",
    encoding="utf-8",
)


XML_DATA_ALT_LABEL = bytes(
    """<?xml version="1.0" encoding="UTF-8"?>
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:skos="http://www.w3.org/2004/02/skos/core#" xmlns:ns5="http://publications.europa.eu/ontology/euvoc#" xmlns:ns6="http://www.w3.org/2008/05/skos-xl#" xmlns:dc="http://purl.org/dc/elements/1.1/">
        <rdf:Description rdf:about="http://data.europa.eu/8mn/euroscivoc/87ff3577-527a-4a40-9c76-2f9d3075e2ba">
        <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/>
        <dcterms:created rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2019-12-02</dcterms:created>
        <dcterms:modified rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2019-12-02</dcterms:modified>
        <owl:versionInfo>1.1.0</owl:versionInfo>
        <skos:inScheme rdf:resource="http://data.europa.eu/8mn/euroscivoc/40c0f173-baa3-48a3-9fe6-d6e8fb366a00"/>
        <ns5:startDate rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2019-12-02</ns5:startDate>
        <skos:notation>87ff3577-527a-4a40-9c76-2f9d3075e2ba</skos:notation>
        <skos:notation>1717</skos:notation>
        <ns5:status rdf:resource="http://publications.europa.eu/resource/authority/concept-status/CURRENT"/>
        <ns5:xlNotation rdf:resource="http://data.europa.eu/8mn/euroscivoc/7f282340-9125-4b0d-aceb-23389311e306"/>
        <ns5:xlNotation rdf:resource="http://data.europa.eu/8mn/euroscivoc/notation_6014c8c4f809ee00ced00312669d98ad"/>
        <skos:altLabel xml:lang="en">broadcastingsatellite service</skos:altLabel>
        <skos:altLabel xml:lang="en">satellite radio system</skos:altLabel>
        <skos:broader rdf:resource="http://data.europa.eu/8mn/euroscivoc/d913bd42-e79c-46a7-8714-14f2a6a0d82f"/>
        <dc:identifier>87ff3577-527a-4a40-9c76-2f9d3075e2ba</dc:identifier>
        <owl:deprecated rdf:datatype="http://www.w3.org/2001/XMLSchema#boolean">false</owl:deprecated>
        </rdf:Description>
        <rdf:Description rdf:about="http://data.europa.eu/8mn/euroscivoc/d913bd42-e79c-46a7-8714-14f2a6a0d82f">
        <skos:narrower rdf:resource="http://data.europa.eu/8mn/euroscivoc/87ff3577-527a-4a40-9c76-2f9d3075e2ba"/>
        </rdf:Description>
</rdf:RDF>""",
    encoding="utf-8",
)


@pytest.fixture(scope="module")
def expected_from_rdf_pref_label_with_parent():
    return [
        {
            "id": "euroscivoc:1717",
            "scheme": "EuroSciVoc",
            "subject": "Satellite radio",
            "title": {
                "it": "Radio satellitare",
                "pl": "Radio satelitarne",
                "fr": "Radio satellite",
                "es": "Radio por satélite",
                "de": "Satellitenfunk",
                "en": "Satellite radio",
            },
            "props": {"parents": "euroscivoc:1225"},
            "identifiers": [
                {
                    "scheme": "url",
                    "identifier": "http://data.europa.eu/8mn/euroscivoc/87ff3577-527a-4a40-9c76-2f9d3075e2ba",
                }
            ],
        },
        {
            "id": "euroscivoc:1225",
            "scheme": "EuroSciVoc",
            "subject": "Radio channel",
            "title": {"en": "Radio channel"},
            "props": {},
            "identifiers": [
                {
                    "scheme": "url",
                    "identifier": "http://data.europa.eu/8mn/euroscivoc/d913bd42-e79c-46a7-8714-14f2a6a0d82f",
                }
            ],
        },
    ]


@pytest.fixture(scope="module")
def expected_from_rdf_alt_label_without_parent():
    return {
        "id": "euroscivoc:1717",
        "scheme": "EuroSciVoc",
        "subject": "Broadcastingsatellite service",
        "title": {"en": "Broadcastingsatellite service"},
        "props": {},
        "identifiers": [
            {
                "scheme": "url",
                "identifier": "http://data.europa.eu/8mn/euroscivoc/87ff3577-527a-4a40-9c76-2f9d3075e2ba",
            }
        ],
    }


def test_euroscivoc_subjects_transformer_pref_label(
    expected_from_rdf_pref_label_with_parent,
):
    reader = RDFReader()
    rdf_data = io.BytesIO(XML_DATA_PREF_LABEL)
    rdf_graph = Graph()
    rdf_graph.parse(rdf_data, format="xml")
    stream_entries = list(reader._iter(rdf_graph))
    assert len(stream_entries) > 0
    transformer = EuroSciVocSubjectsTransformer()
    result = []
    for entry in stream_entries:
        entry = transformer.apply(StreamEntry(entry)).entry
        result.append(entry)
    assert expected_from_rdf_pref_label_with_parent == result


def test_euroscivoc_subjects_transformer_alt_label(
    expected_from_rdf_alt_label_without_parent,
):
    reader = RDFReader()
    rdf_data = io.BytesIO(XML_DATA_ALT_LABEL)
    rdf_graph = Graph()
    rdf_graph.parse(rdf_data, format="xml")
    stream_entries = list(reader._iter(rdf_graph))
    assert len(stream_entries) > 0
    transformer = EuroSciVocSubjectsTransformer()
    for entry in stream_entries:
        result = transformer.apply(StreamEntry(entry))
        assert expected_from_rdf_alt_label_without_parent == result.entry
