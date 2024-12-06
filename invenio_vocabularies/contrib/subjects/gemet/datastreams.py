# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""GEMET subjects datastreams, readers, transformers, and writers."""

from invenio_vocabularies.datastreams.transformers import RDFTransformer

from ..config import gemet_file_url

# Available with the "rdf" extra
try:
    import rdflib
except ImportError:
    rdflib = None


class GEMETSubjectsTransformer(RDFTransformer):
    """
    Transformer class to convert GEMET RDF data to a dictionary format.

    Input:
        - Relevant fields:
            - `skos:prefLabel`: Preferred labels with language codes.
            - `skos:broader`: References to broader concepts (parent concepts).
            - `skos:memberOf`: References to groups or themes the concept belongs to.

    Output:
        - A dictionary with the following structure:
            {
                "id": "gemet:concept/10008",  # GEMET-specific concept ID (skos:Concept).
                "scheme": "GEMET",  # The scheme name indicating this is a GEMET concept.
                "subject": "Consumer product",  # The subject label (first preferred label in English, skos:prefLabel).
                "title": {
                    "en": "Consumer product",  # English label for the concept (skos:prefLabel).
                    "ar": "منتج استهلاكي"  # Arabic label for the concept (skos:prefLabel).
                },
                "props": {
                    "parents": "gemet:concept/6660",  # The parent concept (skos:broader), identified by its GEMET Concept ID.
                    "groups": ["http://www.eionet.europa.eu/gemet/group/10112"],  # Group the concept belongs to (skos:memberOf)(skos:prefLabel).
                    "themes": [
                        "http://www.eionet.europa.eu/gemet/theme/27",  # Theme the concept belongs to (skos:memberOf)(rdfs:label).
                    ]
                },
                "identifiers": [
                    {
                        "scheme": "url",  # Type of identifier (URL).
                        "identifier": "http://www.eionet.europa.eu/gemet/concept/10008"  # URI of the concept (rdf:about).
                    }
                ]
            }
    """

    def _get_parent_notation(self, broader, rdf_graph):
        """Extract parent notation from GEMET URI."""
        return "/".join(broader.split("/")[-2:])

    def _get_groups_and_themes(self, subject, rdf_graph):
        """Extract groups and themes for a subject."""
        groups = []
        themes = []

        for relation in rdf_graph.subjects(
            predicate=self.skos_core.member, object=subject
        ):
            relation_uri = str(relation)
            relation_label = None

            # If the relation is a group, check for skos:prefLabel
            if "group" in relation_uri:
                labels = rdf_graph.objects(
                    subject=relation, predicate=self.skos_core.prefLabel
                )
                relation_label = next(
                    (str(label) for label in labels if label.language == "en"), None
                )
                groups.append(relation_uri)

            # If the relation is a theme, check for rdfs:label
            elif "theme" in relation_uri:
                labels = rdf_graph.objects(
                    subject=relation, predicate=rdflib.RDFS.label
                )
                relation_label = next(
                    (str(label) for label in labels if label.language == "en"), None
                )
                themes.append(relation_uri)

        return groups, themes

    def _transform_entry(self, subject, rdf_graph):
        """Transform an entry to the required dictionary format."""
        concept_number = "/".join(subject.split("/")[-2:])
        id = f"gemet:{concept_number}" if concept_number else None
        labels = self._get_labels(subject, rdf_graph)
        parents = ",".join(
            f"gemet:{n}" for n in reversed(self._find_parents(subject, rdf_graph)) if n
        )
        identifiers = [{"scheme": "url", "identifier": str(subject)}]
        groups, themes = self._get_groups_and_themes(subject, rdf_graph)

        props = {"parents": parents} if parents else {}

        if groups:
            props["groups"] = groups
        if themes:
            props["themes"] = themes

        return {
            "id": id,
            "scheme": "GEMET",
            "subject": labels.get("en", "").capitalize(),
            "title": labels,
            "props": props,
            "identifiers": self._get_identifiers(subject),
        }


# Configuration for datastream

VOCABULARIES_DATASTREAM_TRANSFORMERS = {"gemet-transformer": GEMETSubjectsTransformer}

DATASTREAM_CONFIG = {
    "readers": [
        {
            "type": "http",
            "args": {
                "origin": gemet_file_url,
            },
        },
        {"type": "gzip"},
        {"type": "rdf"},
    ],
    "transformers": [{"type": "gemet-transformer"}],
    "writers": [{"args": {"writer": {"type": "subjects-service"}}, "type": "async"}],
}
