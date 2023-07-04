# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Data Streams transformers tests."""

import pytest

from invenio_vocabularies.datastreams import StreamEntry
from invenio_vocabularies.datastreams.errors import TransformerError
from invenio_vocabularies.datastreams.transformers import XMLTransformer


@pytest.fixture(scope="module")
def expected_from_xml():
    return {
        "field_one": "value",
        "multi_field": {"some": "value", "another": "value too"},
    }


def test_xml_transformer(expected_from_xml):
    bytes_xml_entry = StreamEntry(
        bytes(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            "<record:record>\n"
            "    <field_one:field_one>value</field_one:field_one>\n"
            "    <multi_field:multi_field>\n"
            "        <some:some>value</some:some>\n"
            "        <another:another>value too</another:another>\n"
            "    </multi_field:multi_field>\n"
            "</record:record>\n",
            encoding="raw_unicode_escape",
        )
    )

    transformer = XMLTransformer()
    assert expected_from_xml == transformer.apply(bytes_xml_entry).entry


def test_bad_xml_transformer():
    bytes_xml_entry = StreamEntry(
        bytes(
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            "<field_one:field_one>value</field_one:field_one>\n"
            "<multi_field:multi_field>\n"
            "    <some:some>value</some:some>\n"
            "    <another:another>value too</another:another>\n"
            "</multi_field:multi_field>\n",
            encoding="raw_unicode_escape",
        )
    )

    transformer = XMLTransformer()
    with pytest.raises(TransformerError):
        transformer.apply(bytes_xml_entry)
