# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Datasources module."""


from lxml import etree


class BaseDataSource:

    def __init__(self, *args, **kwargs):
        pass

    def iter_entries(self, *args, **kwargs):
        pass

    def transform_entry(self, *args, **kwargs):
        pass

    def count(self, *args, **kwargs):
        pass


class XMLDataSource(BaseDataSource):
    def __init__(self, source, *args, **kwargs):
        self.source = source

    @staticmethod
    def _xml_to_etree(xml_input):
        """Converts xml to a lxml etree."""
        f = open(xml_input, 'rb')
        xml = f.read()
        f.close()

        return etree.HTML(xml)

    @classmethod
    def _etree_to_dict(cls, tree, only_child):
        """Converts an lxml etree into a dictionary."""
        mydict = dict([(item[0], item[1]) for item in tree.items()])
        children = tree.getchildren()
        if children:
            if len(children) > 1:
                mydict['children'] = [cls._etree_to_dict(child, False) for child in children]
            else:
                child = children[0]
                mydict[child.tag] = cls._etree_to_dict(child, True)
        if only_child:
            return mydict
        else:
            return {tree.tag: mydict}
