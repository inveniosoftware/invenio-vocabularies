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

    SKOS_CORE = Namespace("http://www.w3.org/2004/02/skos/core#")

    def _get_notation(self, subject, rdf_graph):
        """Extract the numeric notation for a subject, ignoring UUID-style notations."""
        for _, _, notation in rdf_graph.triples(
            (subject, self.SKOS_CORE.notation, None)
        ):
            notation_str = str(notation)
            if notation_str.isdigit():
                return notation_str
        return None

    def _get_labels(self, subject, rdf_graph):
        """Extract prefLabel and altLabel languages for a subject."""
        labels = {}
        for _, _, label in rdf_graph.triples((subject, self.SKOS_CORE.prefLabel, None)):
            labels[label.language] = label.value

        if "en" not in labels:
            for _, _, label in rdf_graph.triples(
                (subject, self.SKOS_CORE.altLabel, None)
            ):
                if label.language not in labels:
                    labels[label.language] = label.value

        return labels

    def _find_parents(self, subject, rdf_graph):
        """Find the parent notations of a subject."""
        parents = []
        previous_parent = None

        while True:
            broader_found = False
            for _, _, parent in rdf_graph.triples(
                (subject, self.SKOS_CORE.broader, None)
            ):
                if previous_parent is not None:
                    parents.append(self._get_notation(previous_parent, rdf_graph))
                previous_parent = parent
                subject = parent
                broader_found = True
                break

            if not broader_found:
                if previous_parent is not None:
                    parents.append(self._get_notation(previous_parent, rdf_graph))
                break

        return parents

    def _transform_entry(self, subject, rdf_graph):
        """Transform an entry to the required dictionary format."""
        Entry = namedtuple(
            "Entry", ["id", "scheme", "subject", "title", "identifiers", "props"]
        )

        # Get subject notation with euroscivoc prefix
        notation = self._get_notation(subject, rdf_graph)
        id = f"euroscivoc:{notation}" if notation else None

        # Get labels for the current subject
        languages = self._get_labels(subject, rdf_graph)
        pref_label = languages.get("en", "")

        # Find parent notations in order from top parent to lowest
        parent_notations = self._find_parents(subject, rdf_graph)

        parents = [
            f"euroscivoc:{notation}"
            for notation in reversed(parent_notations)
            if notation is not None
        ]

        # Store parent notations with euroscivoc prefix in props
        props = {}
        if parents:
            props["parents"] = parents

        # Create identifiers list
        identifiers = [{"scheme": "url", "identifier": str(subject)}]
        return Entry(
            id, "EuroSciVoc", pref_label.capitalize(), languages, identifiers, props
        )

    def _as_dict(self, entry):
        """Convert an entry to a dictionary."""
        return {
            "id": entry.id,
            "scheme": entry.scheme,
            "subject": entry.subject,
            "title": entry.title,
            "props": entry.props,
            "identifiers": entry.identifiers,
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
        stream_entry.entry = self._as_dict(entry_data)
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
