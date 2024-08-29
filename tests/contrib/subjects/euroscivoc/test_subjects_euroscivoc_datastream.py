import io
import unittest
from unittest.mock import Mock, patch

import pytest
from rdflib import RDF, Graph, Namespace, URIRef

from invenio_vocabularies.contrib.subjects.euroscivoc.datastreams import (  # Adjust import based on your module name
    EuroSciVocSubjectsHTTPReader,
    EuroSciVocSubjectsTransformer,
)
from invenio_vocabularies.datastreams.datastreams import StreamEntry
from invenio_vocabularies.datastreams.errors import ReaderError, TransformerError

XML_DATA_PREF_LABEL = bytes(
    """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about="http://data.europa.eu/8mn/euroscivoc/87ff3577-527a-4a40-9c76-2f9d3075e2ba">
        <startDate xmlns="http://publications.europa.eu/ontology/euvoc#" rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2019-12-02</startDate>
        <status xmlns="http://publications.europa.eu/ontology/euvoc#" rdf:resource="http://publications.europa.eu/resource/authority/concept-status/CURRENT"/>
        <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/>
        <altLabel xmlns="http://www.w3.org/2004/02/skos/core#" xml:lang="en">broadcastingsatellite service</altLabel>
        <altLabel xmlns="http://www.w3.org/2004/02/skos/core#" xml:lang="en">satellite radio system</altLabel>
        <prefLabel xmlns="http://www.w3.org/2004/02/skos/core#" xml:lang="de">Satellitenfunk</prefLabel>
        <prefLabel xmlns="http://www.w3.org/2004/02/skos/core#" xml:lang="en">satellite radio</prefLabel>
        <prefLabel xmlns="http://www.w3.org/2004/02/skos/core#" xml:lang="fr">radio satellite</prefLabel>
        <prefLabel xmlns="http://www.w3.org/2004/02/skos/core#" xml:lang="es">radio por satélite</prefLabel>
        <prefLabel xmlns="http://www.w3.org/2004/02/skos/core#" xml:lang="it">radio satellitare</prefLabel>
        <prefLabel xmlns="http://www.w3.org/2004/02/skos/core#" xml:lang="pl">radio satelitarne</prefLabel>
    </rdf:Description>
</rdf:RDF>""",
    encoding="utf-8",
)


XML_DATA_ALT_LABEL = bytes(
    """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about="http://data.europa.eu/8mn/euroscivoc/87ff3577-527a-4a40-9c76-2f9d3075e2ba">
        <startDate xmlns="http://publications.europa.eu/ontology/euvoc#" rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2019-12-02</startDate>
        <status xmlns="http://publications.europa.eu/ontology/euvoc#" rdf:resource="http://publications.europa.eu/resource/authority/concept-status/CURRENT"/>
        <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/>
        <altLabel xmlns="http://www.w3.org/2004/02/skos/core#" xml:lang="en">broadcastingsatellite service</altLabel>
        <altLabel xmlns="http://www.w3.org/2004/02/skos/core#" xml:lang="en">satellite radio system</altLabel>
    </rdf:Description>
</rdf:RDF>""",
    encoding="utf-8",
)


@pytest.fixture(scope="module")
def expected_from_rdf_pref_label():
    return {
        "id": "http://data.europa.eu/8mn/euroscivoc/87ff3577-527a-4a40-9c76-2f9d3075e2ba",
        "scheme": "EuroSciVoc",
        "subject": "satellite radio",
        "title": {
            "de": "Satellitenfunk",
            "en": "satellite radio",
            "fr": "radio satellite",
            "es": "radio por satélite",
            "it": "radio satellitare",
            "pl": "radio satelitarne",
        },
    }


@pytest.fixture(scope="module")
def expected_from_rdf_alt_label():
    return {
        "id": "http://data.europa.eu/8mn/euroscivoc/87ff3577-527a-4a40-9c76-2f9d3075e2ba",
        "scheme": "EuroSciVoc",
        "subject": "broadcastingsatellite service",
        "title": {"en": "broadcastingsatellite service"},
    }


def test_euroscivoc_subjects_transformer_pref_label(expected_from_rdf_pref_label):
    reader = EuroSciVocSubjectsHTTPReader()
    rdf_data = io.BytesIO(XML_DATA_PREF_LABEL)
    rdf_graph = Graph()
    rdf_graph.parse(rdf_data, format="xml")
    stream_entries = list(reader._iter(rdf_graph))
    assert len(stream_entries) > 0
    transformer = EuroSciVocSubjectsTransformer()
    for entry in stream_entries:
        result = transformer.apply(StreamEntry(entry))
        assert expected_from_rdf_pref_label == result.entry


def test_euroscivoc_subjects_transformer_alt_label(expected_from_rdf_alt_label):
    reader = EuroSciVocSubjectsHTTPReader()
    rdf_data = io.BytesIO(XML_DATA_ALT_LABEL)
    rdf_graph = Graph()
    rdf_graph.parse(rdf_data, format="xml")
    stream_entries = list(reader._iter(rdf_graph))
    assert len(stream_entries) > 0
    transformer = EuroSciVocSubjectsTransformer()
    for entry in stream_entries:
        result = transformer.apply(StreamEntry(entry))
        assert expected_from_rdf_alt_label == result.entry
