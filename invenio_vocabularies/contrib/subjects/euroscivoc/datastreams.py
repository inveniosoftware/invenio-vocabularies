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
    """Transformer class to convert EuroSciVoc RDF data to a dictionary format."""

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
        identifiers = [{"scheme": "url", "identifier": str(subject)}]

        return {
            "id": id,
            "scheme": "EuroSciVoc",
            "subject": labels.get("en", "").capitalize(),
            "title": labels,
            "props": {"parents": parents} if parents else {},
            "identifiers": identifiers,
        }


# Configuration for datastream transformers, and writers
VOCABULARIES_DATASTREAM_READERS = {}
VOCABULARIES_DATASTREAM_WRITERS = {}

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
    "writers": [
        {
            "type": "subjects-service",
        }
    ],
}
