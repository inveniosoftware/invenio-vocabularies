# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""EuroSciVoc subjects datastreams, readers, transformers, and writers."""

from invenio_vocabularies.datastreams.transformers import RDFTransformer

from ..config import euroscivoc_file_url


class EuroSciVocSubjectsTransformer(RDFTransformer):
    """
     Transformer class to convert EuroSciVoc RDF data to a dictionary format.

     Input:
         - Relevant fields:
             - `skos:notation`: Primary identifier for the concept.
             - `skos:prefLabel`: Preferred labels with language codes.
             - `skos:altLabel`: Alternative labels.
             - `skos:broader`: Broader concepts that this concept belongs to.

    Output:
         {
             "id": "euroscivoc:1717",  # EuroSciVoc-specific concept ID (skos:notation).
             "scheme": "EuroSciVoc",  # The scheme name indicating this is a EuroSciVoc concept.
             "subject": "Satellite radio",  # The primary subject label (first preferred label in English, skos:prefLabel).
             "title": {
                 "it": "Radio satellitare",  # Italian preferred label (skos:prefLabel).
                 "en": "Satellite radio",  # English preferred label (skos:prefLabel).
             },
             "props": {
                 "parents": "euroscivoc:1225",  # The broader concept (skos:broader), identified by its EuroSciVoc Concept ID.
             },
             "identifiers": [
                 {
                     "scheme": "url",  # Type of identifier (URL).
                     "identifier": "http://data.europa.eu/8mn/euroscivoc/87ff3577-527a-4a40-9c76-2f9d3075e2ba",  # URI of the concept (rdf:about).
                 }
             ],
         }
    """

    def _get_notation(self, subject, rdf_graph):
        """Extract the numeric notation for a subject."""
        for _, _, notation in rdf_graph.triples(
            (subject, self.skos_core.notation, None)
        ):
            if str(notation).isdigit():
                return str(notation)
        return None

    def _get_parent_notation(self, broader, rdf_graph):
        """Extract parent notation using numeric notation."""
        return self._get_notation(broader, rdf_graph)

    def _transform_entry(self, subject, rdf_graph):
        notation = self._get_notation(subject, rdf_graph)
        id = f"euroscivoc:{notation}" if notation else None
        labels = self._get_labels(subject, rdf_graph)
        parents = ",".join(
            f"euroscivoc:{n}"
            for n in reversed(self._find_parents(subject, rdf_graph))
            if n
        )

        return {
            "id": id,
            "scheme": "EuroSciVoc",
            "subject": labels.get("en", "").capitalize(),
            "title": labels,
            "props": {"parents": parents} if parents else {},
            "identifiers": self._get_identifiers(subject),
        }


# Configuration for datastream

VOCABULARIES_DATASTREAM_TRANSFORMERS = {
    "euroscivoc-transformer": EuroSciVocSubjectsTransformer
}

DATASTREAM_CONFIG = {
    "readers": [
        {
            "type": "http",
            "args": {
                "origin": euroscivoc_file_url,
            },
        },
        {
            "type": "rdf",
        },
    ],
    "transformers": [{"type": "euroscivoc-transformer"}],
    "writers": [{"args": {"writer": {"type": "subjects-service"}}, "type": "async"}],
}
