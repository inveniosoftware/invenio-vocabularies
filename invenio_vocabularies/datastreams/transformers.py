# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Transformers module."""

from abc import ABC, abstractmethod

from lxml import etree

from .errors import TransformerError
from .xml import etree_to_dict


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
