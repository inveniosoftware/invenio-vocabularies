# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""XML utils."""

from collections import defaultdict


def etree_to_dict(tree):
    """Convert an ElementTree to a dictionary."""
    tag = tree.tag.split(":")[-1]  # strip namespace
    d = {tag: {} if tree.attrib else None}
    children = list(tree)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if tree.attrib:
        d[tag].update(("@" + k, v) for k, v in tree.attrib.items())
    if tree.text:
        text = tree.text.strip()
        if children or tree.attrib:
            if text:
                d[tag]["#text"] = text
        else:
            d[tag] = text
    return d
