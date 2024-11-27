# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""BODC subjects datastreams, readers, transformers, and writers."""

from rdflib.namespace import OWL, RDFS

from invenio_vocabularies.datastreams.readers import RDFReader
from invenio_vocabularies.datastreams.transformers import RDFTransformer

from ..config import bodc_puv_file_url


class BODCPUVSubjectsTransformer(RDFTransformer):
    """Transformer class to convert BODC-PUV RDF data to a dictionary format."""

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
        subject_data = self._get_subject_data(rdf_graph, subject)
        deprecated = subject_data.get(str(OWL.deprecated), [False])
        if deprecated and str(deprecated[0]).lower() == "true":
            return None  # Skip deprecated subjects

        notation = subject_data.get(str(self.skos_core.notation), [])
        id = notation[0] if notation else None

        labels = {
            obj.language: obj.value.capitalize()
            for obj in subject_data.get(str(self.skos_core.prefLabel), [])
            if obj.language and "-" not in obj.language
        }
        alt_labels = [obj for obj in subject_data.get(str(self.skos_core.altLabel), [])]
        subject_text = alt_labels[0] if alt_labels else None

        identifiers = [{"scheme": "url", "identifier": str(subject)}]
        props = {}

        return {
            "id": id,
            "scheme": "BODC-PUV",
            "subject": subject_text,
            "title": labels,
            "props": props,
            "identifiers": identifiers,
        }


# Configuration for datastream transformers, and writers
VOCABULARIES_DATASTREAM_READERS = {}
VOCABULARIES_DATASTREAM_WRITERS = {}

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
