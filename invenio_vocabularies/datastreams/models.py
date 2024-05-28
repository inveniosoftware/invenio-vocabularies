# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 University of Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Record Model for Scythe."""

from invenio_oaipmh_scythe.models import Record
from lxml import etree


class OAIRecord(Record):
    """An XML unpacking implementation for more complicated formats."""

    def get_metadata(self):
        """Extract and return the record's metadata as a dictionary."""
        return xml_to_dict(
            self.xml.find(".//" + self._oai_namespace + "metadata").getchildren()[0],
        )


def xml_to_dict(tree: etree._Element):
    """Convert an XML tree to a dictionary.

    This function takes an XML element tree and converts it into a dictionary.

    Args:
        tree: The root element of the XML tree to be converted.

    Returns:
        A dictionary with the key "record".
    """
    dict_obj = dict()
    dict_obj["record"] = etree.tostring(tree)

    return dict_obj
