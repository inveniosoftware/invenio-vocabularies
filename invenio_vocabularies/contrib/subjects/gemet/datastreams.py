import io
from collections import namedtuple

import requests
from rdflib import OWL, RDF, Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDFS
import gzip
from invenio_vocabularies.config import SUBJECTS_EUROSCIVOC_FILE_URL
from invenio_vocabularies.datastreams.readers import BaseReader
from invenio_vocabularies.datastreams.transformers import BaseTransformer


class GEMETSubjectsHTTPReader(BaseReader):
    """Reader class to fetch and process GEMET RDF data."""

    def __init__(self, origin=None, mode="r", since=None, *args, **kwargs):
        """Initialize the reader with the data source.

        :param origin: The URL from which to fetch the RDF data.
        :param mode: Mode of operation (default is 'r' for reading).
        """
        self.origin = 'https://www.eionet.europa.eu/gemet/latest/gemet.rdf.gz'
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
        """Fetch and process the GEMET RDF data, yielding it one subject at a time.

        :param item: The RDF data provided as bytes (optional).
        :yield: Processed GEMET subject data.
        """
        if item:
            raise NotImplementedError(
                "GEMETSubjectsHTTPReader does not support being chained after another reader"
            )
        # Fetch the RDF data from the specified origin URL
        response = requests.get(self.origin)
        response.raise_for_status()  # Check for HTTP errors

        # Decompress the gzipped content
        with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as gzipped_file:
            rdf_content = gzipped_file.read().decode('utf-8')

        # Parse the decompressed RDF content
        rdf_graph = Graph()
        rdf_graph.parse(io.StringIO(rdf_content), format="xml")

        # Yield each processed subject from the RDF graph
        yield from self._iter(rdf_graph)


class GEMETSubjectsTransformer(BaseTransformer):
    """Transformer class to convert GEMET RDF data to a dictionary format."""

    SKOS_CORE = Namespace("http://www.w3.org/2004/02/skos/core#")
    SPLITCHAR = ","

    def _get_labels(self, subject, rdf_graph):
        """Extract prefLabel and altLabel languages for a subject, excluding languages with a hyphen in the code."""
        labels = {
            label.language: label.value.capitalize()
            for _, _, label in rdf_graph.triples(
                (subject, self.SKOS_CORE.prefLabel, None)
            )
            if '-' not in label.language  # Exclude languages with a hyphen in the code
        }

        if "en" not in labels:
            for _, _, label in rdf_graph.triples(
                (subject, self.SKOS_CORE.altLabel, None)
            ):
                # Only set labels if the language doesn't contain a hyphen
                if '-' not in label.language:
                    labels.setdefault(label.language, label.value.capitalize())
                    
        return labels


    def _find_parents(self, subject, rdf_graph):
        """Find parent notations."""
        parents = []

        # Traverse the broader hierarchy
        for broader in rdf_graph.transitive_objects(subject, self.SKOS_CORE.broader):
            if broader != subject:  # Ensure we don't include the current subject
                parent_notation = '/'.join(broader.split('/')[-2:])
                if parent_notation:
                    parents.append(parent_notation)

        return parents

    def _get_groups_and_themes(self, subject, rdf_graph):
        """Extract groups and themes for a subject."""
        groups = []
        themes = []

        for relation in rdf_graph.subjects(predicate=self.SKOS_CORE.member, object=URIRef(subject)):
            relation_uri = str(relation)
            relation_label = None

            # If the relation is a group, check for skos:prefLabel
            if "group" in relation_uri:
                labels = rdf_graph.objects(subject=relation, predicate=self.SKOS_CORE.prefLabel)
                relation_label = next((str(label) for label in labels if label.language == "en"), None)

            # If the relation is a theme, check for rdfs:label
            elif "theme" in relation_uri:
                labels = rdf_graph.objects(subject=relation, predicate=RDFS.label)
                relation_label = next((str(label) for label in labels if label.language == "en"), None)

            # Add to themes or groups list
            if "theme" in relation_uri:
                themes.append(relation_uri)
            else:
                groups.append(relation_uri)

        return groups, themes



    def _transform_entry(self, subject, rdf_graph):
        """Transform an entry to the required dictionary format."""
        concept_number = '/'.join(subject.split('/')[-2:])
        id = f"gemet:{concept_number}" if concept_number else None
        labels = self._get_labels(subject, rdf_graph)
        parents = self.SPLITCHAR.join(
            f"gemet:{n}" for n in reversed(self._find_parents(subject, rdf_graph))
        )
        identifiers = [{"scheme": "url", "identifier": str(subject)}]
        groups, themes = self._get_groups_and_themes(subject, rdf_graph)

        props = {"parents": parents} if parents else {}

        if groups:
            props["groups"] = groups
        if themes:
            props["themes"] = themes
        x = {
            "id": id,
            "scheme": "GEMET",
            "subject": labels.get("en", "").capitalize(),
            "title": labels,
            "props": props,
            "identifiers": identifiers,
        }

        return {
            "id": id,
            "scheme": "GEMET",
            "subject": labels.get("en", "").capitalize(),
            "title": labels,
            "props": props,
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
VOCABULARIES_DATASTREAM_READERS = {"gemet-reader": GEMETSubjectsHTTPReader}

VOCABULARIES_DATASTREAM_WRITERS = {}

VOCABULARIES_DATASTREAM_TRANSFORMERS = {
    "gemet-transformer": GEMETSubjectsTransformer
}

DATASTREAM_CONFIG = {
    "readers": [
        {
            "type": "gemet-reader",
        }
    ],
    "transformers": [{"type": "gemet-transformer"}],
    "writers": [
        {
            "type": "subjects-service",
        }
    ],
}
