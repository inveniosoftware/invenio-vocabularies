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

from invenio_vocabularies.config import SUBJECTS_EUROSCIVOC_FILE_URL
from invenio_vocabularies.datastreams.readers import BaseReader
from invenio_vocabularies.datastreams.transformers import BaseTransformer


class EuroSciVocSubjectsHTTPReader(BaseReader):
    """Reader class to fetch and process EuroSciVoc RDF data."""

    def __init__(self, origin=None, mode="r", since=None, *args, **kwargs):
        """Initialize the reader with the data source.

        :param origin: The URL from which to fetch the RDF data.
        :param mode: Mode of operation (default is 'r' for reading).
        """
        self.origin = origin or SUBJECTS_EUROSCIVOC_FILE_URL
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

    SKOS_CORE = Namespace("http://www.w3.org/2004/02/skos/core#")
    SPLITCHAR = ","

    def _get_notation(self, subject, rdf_graph):
        """Extract the numeric notation for a subject."""
        for _, _, notation in rdf_graph.triples(
            (subject, self.SKOS_CORE.notation, None)
        ):
            if str(notation).isdigit():
                return str(notation)
        return None

    def _get_labels(self, subject, rdf_graph):
        """Extract prefLabel and altLabel languages for a subject."""
        labels = {
            label.language: label.value.capitalize()
            for _, _, label in rdf_graph.triples(
                (subject, self.SKOS_CORE.prefLabel, None)
            )
        }
        if "en" not in labels:
            for _, _, label in rdf_graph.triples(
                (subject, self.SKOS_CORE.altLabel, None)
            ):
                labels.setdefault(label.language, label.value.capitalize())
        return labels

    def _find_parents(self, subject, rdf_graph):
        """Find parent notations."""
        parents = []

        # Traverse the broader hierarchy
        for broader in rdf_graph.transitive_objects(subject, self.SKOS_CORE.broader):
            if broader != subject:  # Ensure we don't include the current subject
                parent_notation = self._get_notation(broader, rdf_graph)
                if parent_notation:
                    parents.append(parent_notation)

        return parents

    def _transform_entry(self, subject, rdf_graph):
        """Transform an entry to the required dictionary format."""
        # Get subject notation with euroscivoc prefix
        notation = self._get_notation(subject, rdf_graph)
        id = f"euroscivoc:{notation}" if notation else None
        # Get labels for the current subject
        labels = self._get_labels(subject, rdf_graph)
        # Join parent notations with SPLITCHAR separator and add euroscivoc prefix
        parents = self.SPLITCHAR.join(
            f"euroscivoc:{n}" for n in reversed(self._find_parents(subject, rdf_graph))
        )
        # Create identifiers list
        identifiers = [{"scheme": "url", "identifier": str(subject)}]

        return {
            "id": id,
            "scheme": "EuroSciVoc",
            "subject": labels.get("en", "").capitalize(),
            "title": labels,
            "props": {"parents": parents} if parents else {},
            "identifiers": identifiers,
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
        stream_entry.entry = entry_data
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
            "type": "subjects-service",
        }
    ],
}
