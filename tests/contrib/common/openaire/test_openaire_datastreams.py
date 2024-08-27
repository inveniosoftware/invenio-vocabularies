# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""OpenAIRE-related Datastreams Readers/Writers/Transformers tests."""

import io
from unittest.mock import patch

import pytest

from invenio_vocabularies.contrib.common.openaire.datastreams import OpenAIREHTTPReader
from invenio_vocabularies.datastreams.errors import ReaderError

API_JSON_RESPONSE_CONTENT = {
    "linkset": [
        {
            "anchor": "https://example.com/records/10488385",
            "item": [
                {
                    "href": "https://example.com/records/10488385/files/organization.tar",
                    "type": "application/x-tar",
                },
                {
                    "href": "https://example.com/records/10488385/files/project.tar",
                    "type": "application/x-tar",
                },
            ],
        },
        {
            "anchor": "https://example.com/api/records/10488385",
            "describes": [
                {"href": "https://example.com/records/10488385", "type": "text/html"}
            ],
            "type": "application/dcat+xml",
        },
    ]
}

API_JSON_RESPONSE_CONTENT_WRONG_NUMBER_PROJECT_TAR_ITEMS_ERROR = {
    "linkset": [
        {
            "anchor": "https://example.com/records/10488385",
            "item": [
                {
                    "href": "https://example.com/records/10488385/files/organization.tar",
                    "type": "application/x-tar",
                },
                {
                    "href": "https://example.com/records/10488385/files/project.tar",
                    "type": "application/x-tar",
                },
                {
                    "href": "https://example.com/another/project.tar",
                    "type": "application/x-tar",
                },
            ],
        },
        {
            "anchor": "https://example.com/api/records/10488385",
            "describes": [
                {"href": "https://example.com/records/10488385", "type": "text/html"}
            ],
            "type": "application/dcat+xml",
        },
    ]
}

DOWNLOAD_FILE_BYTES_CONTENT = b"The content of the file"


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
def test_openaire_http_reader(_, download_file_bytes_content):
    reader = OpenAIREHTTPReader(origin="full", tar_href="/project.tar")
    results = []
    for entry in reader.read():
        results.append(entry)

    assert len(results) == 1
    assert isinstance(results[0], io.BytesIO)
    assert results[0].read() == download_file_bytes_content


@patch(
    "requests.get",
    side_effect=lambda url, headers=None: MockResponse(
        API_JSON_RESPONSE_CONTENT_WRONG_NUMBER_PROJECT_TAR_ITEMS_ERROR
    ),
)
def test_openaire_http_reader_wrong_number_tar_items_error(_):
    reader = OpenAIREHTTPReader(origin="full", tar_href="/project.tar")
    with pytest.raises(ReaderError):
        next(reader.read())


def test_openaire_http_reader_unsupported_origin_option():
    reader = OpenAIREHTTPReader(origin="unsupported_origin_option")
    with pytest.raises(ReaderError):
        next(reader.read())


def test_openaire_http_reader_item_not_implemented():
    reader = OpenAIREHTTPReader()
    with pytest.raises(NotImplementedError):
        next(reader.read("A fake item"))


def test_openaire_http_reader_iter_not_implemented():
    reader = OpenAIREHTTPReader()
    with pytest.raises(NotImplementedError):
        reader._iter("A fake file pointer")
