# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Transformers module."""

from abc import ABC, abstractmethod
from collections import defaultdict

from lxml import etree

from .errors import TransformerError


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

    @classmethod
    def _xml_to_etree(cls, xml):
        """Converts XML to a lxml etree."""
        return etree.HTML(xml)

    @classmethod
    def _etree_to_dict(cls, tree):
        d = {tree.tag: {} if tree.attrib else None}
        children = list(tree)
        if children:
            dd = defaultdict(list)
            for dc in map(cls._etree_to_dict, children):
                for k, v in dc.items():
                    dd[k].append(v)
            d = {tree.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
        if tree.attrib:
            d[tree.tag].update(("@" + k, v) for k, v in tree.attrib.items())
        if tree.text:
            text = tree.text.strip()
            if children or tree.attrib:
                if text:
                    d[tree.tag]["#text"] = text
            else:
                d[tree.tag] = text
        return d

    def apply(self, stream_entry, **kwargs):
        """Applies the transformation to the stream entry.

        Requires the root element to be named "record".
        """
        xml_tree = self._xml_to_etree(stream_entry.entry)
        record = self._etree_to_dict(xml_tree)["html"]["body"].get("record")

        if not record:
            raise TransformerError(f"Record not found in XML entry.")

        stream_entry.entry = record
        return stream_entry
