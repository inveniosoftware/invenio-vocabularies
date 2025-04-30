# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""ROR-related Datastreams Readers/Writers/Transformers tests."""

import io
from unittest.mock import patch

import pytest
from flask import Flask

from invenio_vocabularies.contrib.common.ror.datastreams import (
    RORHTTPReader,
    RORTransformer,
)
from invenio_vocabularies.datastreams.errors import ReaderError

API_JSON_RESPONSE_CONTENT = {
    "linkset": [
        {
            "anchor": "https://zenodo.org/records/11186879",
            "describedby": [
                {
                    "href": "https://zenodo.org/api/records/11186879",
                    "type": "application/ld+json",
                },
            ],
            "item": [
                {
                    "href": "https://example.com/records/11186879/files/v1.46.1-2024-05-13-ror-data.zip",
                    "type": "application/zip",
                }
            ],
            "type": [{"href": "https://schema.org/Dataset"}],
        },
        {
            "anchor": "https://example.com/records/11186879/files/v1.46.1-2024-05-13-ror-data.zip",
            "collection": [
                {"href": "https://zenodo.org/records/11186879", "type": "text/html"}
            ],
        },
        {
            "anchor": "https://zenodo.org/api/records/11186879",
            "describes": [
                {"href": "https://zenodo.org/records/11186879", "type": "text/html"}
            ],
        },
    ]
}

API_JSON_RESPONSE_CONTENT_WITHOUT_JSON_LD = {
    "linkset": [
        {
            "anchor": "https://example.com/records/11186879",
            "item": [
                {
                    "href": "https://example.com/records/11186879/files/v1.46.1-2024-05-13-ror-data.zip",
                    "type": "application/zip",
                }
            ],
            "type": "application/zip",
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


API_JSON_RESPONSE_CONTENT_LD_JSON = {
    "name": "ROR Data",
    "dateCreated": "2024-07-11T22:29:25.727626+00:00",
    "datePublished": "2024-07-11T22:29:25.727626+00:00",
}

DOWNLOAD_FILE_BYTES_CONTENT = b"The content of the file"

DOI_LINKSET_INFO = {
    "linkset": {
        "url": "https://zenodo.org/api/records/12729557",
        "rel": "linkset",
        "type": "application/linkset+json",
    }
}


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
    links = DOI_LINKSET_INFO

    def __init__(self, api_json_response_content, remove_links=False):
        self.api_json_response_content = api_json_response_content
        self.links = DOI_LINKSET_INFO
        if remove_links:
            self.links = {}

    def json(self, **kwargs):
        return self.api_json_response_content

    def raise_for_status(self):
        pass


def side_effect(url, headers=None, allow_redirects=False):
    if not headers:
        return MockResponse({})
    if headers["Accept"] == "application/ld+json":
        return MockResponse(API_JSON_RESPONSE_CONTENT_LD_JSON)
    elif headers["Accept"] == "application/linkset+json":
        return MockResponse(API_JSON_RESPONSE_CONTENT)


@patch("requests.get", side_effect=side_effect)
def test_ror_http_reader(_):
    reader = RORHTTPReader()
    results = []
    app = Flask("testapp")
    with app.app_context():
        for entry in reader.read():
            results.append(entry)

    assert len(results) == 1
    assert isinstance(results[0], io.BytesIO)
    assert results[0].read() == DOWNLOAD_FILE_BYTES_CONTENT


@patch("requests.get", side_effect=side_effect)
def test_ror_http_reader_since_before_publish(_):
    reader = RORHTTPReader(since="2024-07-10")
    results = []
    app = Flask("testapp")
    with app.app_context():
        for entry in reader.read():
            results.append(entry)

    assert len(results) == 1


@patch("requests.get", side_effect=side_effect)
def test_ror_http_reader_since_after_publish(_):
    reader = RORHTTPReader(since="2024-07-12")
    results = []
    app = Flask("testapp")
    with app.app_context():
        for entry in reader.read():
            results.append(entry)

    assert len(results) == 0


@patch(
    "requests.get",
    side_effect=lambda url, headers=None, allow_redirects=False: MockResponse(
        API_JSON_RESPONSE_CONTENT_WRONG_NUMBER_ZIP_ITEMS_ERROR
    ),
)
def test_ror_http_reader_wrong_number_zip_items_error(_):
    reader = RORHTTPReader()
    with pytest.raises(ReaderError):
        next(reader.read())


@patch(
    "requests.get",
    side_effect=lambda url, headers=None, allow_redirects=False: MockResponse(
        API_JSON_RESPONSE_CONTENT_WITHOUT_JSON_LD
    ),
)
def test_ror_http_reader_no_json_ld(_):
    reader = RORHTTPReader(since="2024-07-12")
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
