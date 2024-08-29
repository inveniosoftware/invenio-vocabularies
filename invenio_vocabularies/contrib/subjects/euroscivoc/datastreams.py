# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""EuroSciVoc subjects datastreams, readers, transformers, and writers."""

import io
from collections import namedtuple

import requests
from rdflib import OWL, RDF, Graph, Namespace

from invenio_vocabularies.datastreams.readers import BaseReader
from invenio_vocabularies.datastreams.transformers import BaseTransformer


class EuroSciVocSubjectsHTTPReader(BaseReader):
    """Reader class to fetch and process EuroSciVoc RDF data."""

    def __init__(self, origin=None, mode="r", since=None, *args, **kwargs):
        """Initialize the reader with the data source.

        :param origin: The URL from which to fetch the RDF data.
        :param mode: Mode of operation (default is 'r' for reading).
        """
        self.origin = (
            origin
            or "https://op.europa.eu/o/opportal-service/euvoc-download-handler?cellarURI=http%3A%2F%2Fpublications.europa.eu%2Fresource%2Fdistribution%2Feuroscivoc%2F20231115-0%2Frdf%2Fskos_ap_eu%2FEuroSciVoc-skos-ap-eu.rdf&fileName=EuroSciVoc-skos-ap-eu.rdf"
        )
        super().__init__(origin=origin, mode=mode, *args, **kwargs)

    def _iter(self, rdf_graph):
        """Iterate over the RDF graph, yielding one subject at a time.

        :param rdf_graph: The RDF graph to process.
        :yield: Subject and graph to be transformed.
        """
        SKOS_CORE = Namespace("http://www.w3.org/2004/02/skos/core#")

        for subject, _, _ in rdf_graph.triples((None, RDF.type, SKOS_CORE.Concept)):
            yield {"subject": subject, "rdf_graph": rdf_graph}

    def read(self, item=None, *args, **kwargs):
        """Fetch and process the EuroSciVoc RDF data, yielding it one subject at a time.

        :param item: The RDF data provided as bytes (optional).
        :yield: Processed EuroSciVoc subject data.
        """
        if item:
            raise NotImplementedError(
                "EuroSciVocSubjectsHTTPReader does not support being chained after another reader"
            )
        # Fetch the RDF data from the specified origin URL
        response = requests.get(self.origin)
        response.raise_for_status()

        # Treat the response content as a file-like object
        rdf_data = io.BytesIO(response.content)

        # Parse the RDF data into a graph
        rdf_graph = Graph()
        rdf_graph.parse(rdf_data, format="xml")

        # Yield each processed subject from the RDF graph
        yield from self._iter(rdf_graph)


class EuroSciVocSubjectsTransformer(BaseTransformer):
    """Transformer class to convert EuroSciVoc RDF data to a dictionary format."""

    def _transform_entry(self, subject, rdf_graph):
        """Transform an entry to the required dictionary format."""
        SKOS_CORE = Namespace("http://www.w3.org/2004/02/skos/core#")
        Entry = namedtuple("Entry", ["id", "scheme", "subject", "title", "props"])
        # Initialize entry fields
        languages = {}
        pref_label = None

        for _, _, label in rdf_graph.triples((subject, SKOS_CORE.prefLabel, None)):
            languages[label.language] = label.value
            if label.language == "en":
                pref_label = label.value

        # Fallback to alternative labels if no preferred label in English
        if not pref_label:
            for _, _, label in rdf_graph.triples((subject, SKOS_CORE.altLabel, None)):
                if label.language not in languages:
                    languages[label.language] = label.value
                if label.language == "en":
                    pref_label = label.value
                    break

        title = languages
        entry = Entry(str(subject), "EuroSciVoc", pref_label, title, {})
        return entry

    def _as_dict(self, entry):
        """Convert an entry to a dictionary."""
        return {
            "id": entry.id,
            "scheme": entry.scheme,
            "subject": entry.subject,
            "title": entry.title,
        }

    def apply(self, stream_entry, *args, **kwargs):
        """Transform a stream entry to the required dictionary format.

        :param stream_entry: The entry to be transformed, which includes the subject and the RDF graph.
        :return: The transformed stream entry.
        """
        # Apply transformations
        entry_data = self._transform_entry(
            stream_entry.entry["subject"], stream_entry.entry["rdf_graph"]
        )
        entry_data = self._as_dict(entry_data)
        stream_entry.entry = entry_data  # Update the stream entry with transformed data
        return stream_entry


# Configuration for datastream readers, transformers, and writers
VOCABULARIES_DATASTREAM_READERS = {"euroscivoc-reader": EuroSciVocSubjectsHTTPReader}

VOCABULARIES_DATASTREAM_WRITERS = {}

VOCABULARIES_DATASTREAM_TRANSFORMERS = {
    "euroscivoc-transformer": EuroSciVocSubjectsTransformer
}

DATASTREAM_CONFIG = {
    "readers": [
        {
            "type": "euroscivoc-reader",
        }
    ],
    "transformers": [{"type": "euroscivoc-transformer"}],
    "writers": [
        {
            "args": {"writer": {"args": {"update": True}, "type": "subjects-service"}},
            "type": "async",
        }
    ],
}
