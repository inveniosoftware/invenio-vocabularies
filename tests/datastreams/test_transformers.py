# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
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
        "top_level_field": "top-level single value",
        "top_level_object_field": {
            "some": "value",
            "another": "value too",
            "nested_array_field": {
                "@array_attr": "value",
                "array_element_object": [
                    {
                        "@obj_attr": "first",
                        "element_foo": "value1",
                        "element_bar": "value1",
                    },
                    {
                        "@obj_attr": "second",
                        "element_foo": "value2",
                        "element_bar": "value2",
                        "element_qux": "value2",
                    },
                ],
            },
        },
    }


def test_xml_transformer(expected_from_xml):
    bytes_xml_entry = StreamEntry(
        b"""
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <ns:top_level_field>top-level single value</ns:top_level_field>
        <ns:top_level_object_field>
            <ns:some>value</ns:some>
            <ns:another>value too</ns:another>
            <ns:nested_array_field array_attr="value">
                <ns:array_element_object obj_attr="first">
                    <ns:element_foo>value1</ns:element_foo>
                    <ns:element_bar>value1</ns:element_bar>
                </ns:array_element_object>
                <ns:array_element_object obj_attr="second">
                    <ns:element_foo>value2</ns:element_foo>
                    <ns:element_bar>value2</ns:element_bar>
                    <ns:element_qux>value2</ns:element_qux>
                </ns:array_element_object>
            </ns:nested_array_field array_attr="value">
        </ns:top_level_object_field>
        """
    )

    transformer = XMLTransformer()
    assert expected_from_xml == transformer.apply(bytes_xml_entry).entry


def test_bad_xml_transformer():
    bytes_xml_entry = StreamEntry(
        b"""
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <ns:top_level_field>top-level single value</ns:top_level_field>
        <ns:top_level_object_field>
            <ns:some>value</ns:some>
            <ns:another>value too</ns:another>
            <ns:nested_array_field array_attr="value">
                <ns:array_element_object obj_attr="first">
                    <ns:element_foo>value1</ns:element_foo>
                    <ns:element_bar>value1</ns:element_bar>
                </ns:array_element_object>
                <ns:array_element_object obj_attr="second">
                    <ns:element_foo>value2</ns:element_foo>
                    <ns:element_bar>value2</ns:element_bar>
                    <ns:element_qux>value2</ns:element_qux>
                </ns:array_element_object>
            </ns:nested_array_field array_attr="value">
        </ns:top_level_object_field>
        """
    )

    transformer = XMLTransformer(root_element="field_two")

    with pytest.raises(TransformerError):
        transformer.apply(bytes_xml_entry)
