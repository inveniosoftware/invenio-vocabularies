# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Transformers module."""

from abc import ABC, abstractmethod
from urllib.parse import urlparse

from lxml import etree

from .errors import TransformerError
from .xml import etree_to_dict

try:
    import rdflib
except ImportError:
    rdflib = None


class BaseTransformer(ABC):
    """Base transformer."""

    @abstractmethod
    def apply(self, stream_entry, *args, **kwargs):
        """Applies the transformation to the entry.

        :returns: A StreamEntry. The transformed entry.
                  Raises TransformerError in case of errors.
        """
        pass


class XMLTransformer(BaseTransformer):
    """XML transformer."""

    def __init__(self, root_element=None, *args, **kwargs):
        """Initializes the transformer."""
        self.root_element = root_element
        super().__init__(*args, **kwargs)

    @classmethod
    def _xml_to_etree(cls, xml):
        """Converts XML to a lxml etree."""
        return etree.HTML(xml)

    def apply(self, stream_entry, **kwargs):
        """Applies the transformation to the stream entry.

        Requires the root element to be named "record".
        """
        xml_tree = self._xml_to_etree(stream_entry.entry)
        xml_dict = etree_to_dict(xml_tree)["html"]["body"]

        if self.root_element:
            record = xml_dict.get(self.root_element)
            if not record:
                raise TransformerError(
                    f"Root element '{self.root_element}' not found in XML entry."
                )
        else:
            record = xml_dict

        stream_entry.entry = record
        return stream_entry


class RDFTransformer(BaseTransformer):
    """Base Transformer class for RDF data to dictionary format."""

    @property
    def skos_core(self):
        """Get the SKOS core namespace."""
        return rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")

    def _validate_subject_url(self, subject):
        """Check if the subject is a valid URL."""
        parsed = urlparse(str(subject))
        return bool(parsed.netloc and parsed.scheme)

    def _get_identifiers(self, subject):
        """Generate identifiers field for a valid subject URL."""
        if self._validate_subject_url(subject):
            return [{"scheme": "url", "identifier": str(subject)}]
        return []

    def _get_labels(self, subject, rdf_graph):
        """Extract labels (prefLabel or altLabel) for a subject."""
        labels = {
            label.language: label.value.capitalize()
            for _, _, label in rdf_graph.triples(
                (subject, self.skos_core.prefLabel, None)
            )
            if label.language and "-" not in label.language
        }

        if "en" not in labels:
            for _, _, label in rdf_graph.triples(
                (subject, self.skos_core.altLabel, None)
            ):
                labels.setdefault(label.language, label.value.capitalize())

        return labels

    def _find_parents(self, subject, rdf_graph):
        """Find parent notations."""
        return [
            self._get_parent_notation(broader, rdf_graph)
            for broader in rdf_graph.transitive_objects(subject, self.skos_core.broader)
            if broader != subject
        ]

    def _get_parent_notation(self, broader, rdf_graph):
        """Extract notation for a parent."""
        raise NotImplementedError("This method should be implemented in a subclass.")

    def _transform_entry(self, subject, rdf_graph):
        """Transform an RDF subject entry into the desired dictionary format."""
        raise NotImplementedError("This method should be implemented in a subclass.")

    def apply(self, stream_entry, *args, **kwargs):
        """Apply transformation to a stream entry."""
        stream_entry.entry = self._transform_entry(
            stream_entry.entry["subject"], stream_entry.entry["rdf_graph"]
        )
        return stream_entry
