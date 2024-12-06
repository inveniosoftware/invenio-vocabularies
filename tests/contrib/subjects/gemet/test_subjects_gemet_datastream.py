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

from invenio_vocabularies.contrib.subjects.gemet.datastreams import (
    GEMETSubjectsTransformer,
)
from invenio_vocabularies.datastreams.datastreams import StreamEntry
from invenio_vocabularies.datastreams.readers import RDFReader

XML_DATA = bytes(
    """<?xml version="1.0" encoding="UTF-8"?>
    <rdf:RDF xmlns:skos="http://www.w3.org/2004/02/skos/core#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
         xmlns:dcterms="http://purl.org/dc/terms/"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
         xml:base="http://www.eionet.europa.eu/gemet/">
        <skos:Concept rdf:about="concept/10008">
            <skos:inScheme rdf:resource="http://www.eionet.europa.eu/gemet/gemetThesaurus"/>
            <skos:prefLabel xml:lang="en">Consumer product</skos:prefLabel>
            <skos:prefLabel xml:lang="ar">منتج استهلاكي</skos:prefLabel>
            <skos:broader rdf:resource="concept/6660"/>
            <skos:memberOf rdf:resource="group/10112"/>
            <skos:memberOf rdf:resource="theme/27"/>
            <skos:memberOf rdf:resource="theme/34"/>
        </skos:Concept>
        <rdf:Description rdf:about="theme/27">
            <skos:member rdf:resource="concept/10008"/>
        </rdf:Description>
        <rdf:Description rdf:about="theme/34">
            <skos:member rdf:resource="concept/10008"/>
        </rdf:Description>
        <rdf:Description rdf:about="group/10112">
            <skos:member rdf:resource="concept/10008"/>
        </rdf:Description>
    </rdf:RDF>""",
    encoding="utf-8",
)


@pytest.fixture(scope="module")
def expected_from_rdf():
    return [
        {
            "id": "gemet:concept/10008",
            "scheme": "GEMET",
            "subject": "Consumer product",
            "title": {
                "en": "Consumer product",
                "ar": "منتج استهلاكي",
            },
            "props": {
                "parents": "gemet:concept/6660",
                "groups": ["http://www.eionet.europa.eu/gemet/group/10112"],
                "themes": [
                    "http://www.eionet.europa.eu/gemet/theme/27",
                    "http://www.eionet.europa.eu/gemet/theme/34",
                ],
            },
            "identifiers": [
                {
                    "scheme": "url",
                    "identifier": "http://www.eionet.europa.eu/gemet/concept/10008",
                }
            ],
        }
    ]


def test_gemet_concept_transformer_pref_label(expected_from_rdf):
    reader = RDFReader()
    rdf_data = io.BytesIO(XML_DATA)
    rdf_graph = Graph()
    rdf_graph.parse(rdf_data, format="xml")
    stream_entries = list(reader._iter(rdf_graph))
    assert len(stream_entries) > 0
    transformer = GEMETSubjectsTransformer()
    result = []
    for entry in stream_entries:
        entry = transformer.apply(StreamEntry(entry)).entry
        result.append(entry)
    assert expected_from_rdf == result
