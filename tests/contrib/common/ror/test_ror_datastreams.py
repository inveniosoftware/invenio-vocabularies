# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""ROR-related Datastreams Readers/Writers/Transformers tests."""

import io
from unittest.mock import patch

import pytest

from invenio_vocabularies.contrib.common.ror.datastreams import (
    RORHTTPReader,
    RORTransformer,
)
from invenio_vocabularies.datastreams.errors import ReaderError

API_JSON_RESPONSE_CONTENT = {
    "linkset": [
        {
            "anchor": "https://example.com/records/11186879",
            "item": [
                {
                    "href": "https://example.com/records/11186879/files/v1.46.1-2024-05-13-ror-data.zip",
                    "type": "application/zip",
                }
            ],
        },
        {
            "anchor": "https://example.com/api/records/11186879",
            "describes": [
                {"href": "https://example.com/records/11186879", "type": "text/html"}
            ],
            "type": "application/dcat+xml",
        },
    ]
}

API_JSON_RESPONSE_CONTENT_WRONG_NUMBER_ZIP_ITEMS_ERROR = {
    "linkset": [
        {
            "anchor": "https://example.com/records/11186879",
            "item": [
                {
                    "href": "https://example.com/records/11186879/files/v1.46.1-2024-05-13-ror-data.zip",
                    "type": "application/zip",
                },
                {
                    "href": "https://example.com/another/file.zip",
                    "type": "application/zip",
                },
            ],
        },
        {
            "anchor": "https://example.com/api/records/11186879",
            "describes": [
                {"href": "https://example.com/records/11186879", "type": "text/html"}
            ],
            "type": "application/dcat+xml",
        },
    ]
}

DOWNLOAD_FILE_BYTES_CONTENT = b"The content of the file"


@pytest.fixture(scope="module")
def expected_from_ror_json():
    return {
        "id": "05dxps055",
        "name": "California Institute of Technology",
        "title": {
            "en": "California Institute of Technology",
            "es": "Instituto de Tecnología de California",
        },
        "acronym": "CIT",
        "aliases": ["Caltech"],
        "country": "US",
        "country_name": "United States",
        "location_name": "Pasadena",
        "status": "active",
        "identifiers": [
            {"scheme": "ror", "identifier": "05dxps055"},
        ],
        "types": ["education", "funder"],
    }


class MockResponse:
    content = DOWNLOAD_FILE_BYTES_CONTENT

    def __init__(self, api_json_response_content):
        self.api_json_response_content = api_json_response_content

    def json(self, **kwargs):
        return self.api_json_response_content

    def raise_for_status(self):
        pass


@pytest.fixture(scope="function")
def download_file_bytes_content():
    return DOWNLOAD_FILE_BYTES_CONTENT


@patch(
    "requests.get",
    side_effect=lambda url, headers=None: MockResponse(API_JSON_RESPONSE_CONTENT),
)
def test_ror_http_reader(_, download_file_bytes_content):
    reader = RORHTTPReader()
    results = []
    for entry in reader.read():
        results.append(entry)

    assert len(results) == 1
    assert isinstance(results[0], io.BytesIO)
    assert results[0].read() == download_file_bytes_content


@patch(
    "requests.get",
    side_effect=lambda url, headers=None: MockResponse(
        API_JSON_RESPONSE_CONTENT_WRONG_NUMBER_ZIP_ITEMS_ERROR
    ),
)
def test_ror_http_reader_wrong_number_zip_items_error(_):
    reader = RORHTTPReader()
    with pytest.raises(ReaderError):
        next(reader.read())


def test_ror_http_reader_item_not_implemented():
    reader = RORHTTPReader()
    with pytest.raises(NotImplementedError):
        next(reader.read("A fake item"))


def test_ror_http_reader_iter_not_implemented():
    reader = RORHTTPReader()
    with pytest.raises(NotImplementedError):
        reader._iter("A fake file pointer")


def test_ror_transformer(app, dict_ror_entry, expected_from_ror_json):
    transformer = RORTransformer()
    assert expected_from_ror_json == transformer.apply(dict_ror_entry).entry
