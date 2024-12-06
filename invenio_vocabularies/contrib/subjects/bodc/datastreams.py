# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""BODC subjects datastreams, readers, transformers, and writers."""

from invenio_vocabularies.datastreams.errors import TransformerError
from invenio_vocabularies.datastreams.readers import RDFReader
from invenio_vocabularies.datastreams.transformers import RDFTransformer

from ..config import bodc_puv_file_url

# Available with the "rdf" extra
try:
    import rdflib
except ImportError:
    rdflib = None


class BODCPUVSubjectsTransformer(RDFTransformer):
    """
    Transformer class to convert BODC-PUV RDF data to a dictionary format.

    Input:
        - Relevant fields:
            - `skos:notation`: Primary identifier for the concept.
            - `skos:prefLabel`: Preferred labels with language codes.
            - `skos:altLabel`: Alternative labels (optional).
            - `skos:definition`: Definitions of the concept.
            - `owl:deprecated`: Boolean flag indicating if the concept is deprecated.

    Output:
        - A dictionary with the following structure:
            {
                "id": "SDN:P01::SAGEMSFM",  # BODC-specific parameter ID (skos:notation).
                "scheme": "BODC-PUV",  # The scheme name indicating this is a BODC Parameter Usage Vocabulary concept.
                "subject": "AMSSedAge",  # The alternative label (skos:altLabel), if available, or None.
                "title": {
                    "en": "14C age of Foraminiferida"  # English preferred label (skos:prefLabel).
                },
                "props": {
                    "definitions": "Accelerated mass spectrometry on picked tests",  # Definition of subject (skos:definition).
                },
                "identifiers": [
                    {
                        "scheme": "url",  # Type of identifier (URL).
                        "identifier": "http://vocab.nerc.ac.uk/collection/P01/current/SAGEMSFM"  # URI of the concept.
                    }
                ]
            }
    """

    def _get_subject_data(self, rdf_graph, subject):
        """Fetch all triples for a subject and organize them into a dictionary."""
        data = {}
        for predicate, obj in rdf_graph.predicate_objects(subject=subject):
            predicate_name = str(predicate)
            if predicate_name not in data:
                data[predicate_name] = []
            data[predicate_name].append(obj)
        return data

    def _transform_entry(self, subject, rdf_graph):
        """Transform an entry to the required dictionary format."""
        labels = self._get_labels(subject, rdf_graph)
        subject_data = self._get_subject_data(rdf_graph, subject)
        deprecated = subject_data.get(str(rdflib.namespace.OWL.deprecated), [False])
        if deprecated and str(deprecated[0]).lower() == "true":
            return None  # Skip deprecated subjects

        notation = subject_data.get(str(self.skos_core.notation), [])
        if notation:
            id = str(notation[0])
        else:
            raise TransformerError(f"No id found for: {subject}")

        alt_labels = [obj for obj in subject_data.get(str(self.skos_core.altLabel), [])]
        subject_text = str(alt_labels[0]) if alt_labels else ""
        definition = str(subject_data.get(str(self.skos_core.definition), [None])[0])

        return {
            "id": id,
            "scheme": "BODC-PUV",
            "subject": subject_text,
            "title": labels,
            "props": {"definition": definition} if definition else {},
            "identifiers": self._get_identifiers(subject),
        }


# Configuration for datastream

VOCABULARIES_DATASTREAM_TRANSFORMERS = {"bodc-transformer": BODCPUVSubjectsTransformer}

DATASTREAM_CONFIG = {
    "readers": [
        {
            "type": "http",
            "args": {
                "origin": bodc_puv_file_url,
            },
        },
        {"type": "rdf"},
    ],
    "transformers": [{"type": "bodc-transformer"}],
    "writers": [{"args": {"writer": {"type": "subjects-service"}}, "type": "async"}],
}
