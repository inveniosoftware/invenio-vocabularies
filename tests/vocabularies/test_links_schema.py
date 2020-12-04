# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Tests links schema."""

from invenio_vocabularies.resources.records.schema import SearchLinksSchema, \
    VocabularyLinksSchema


class MockResourceRequestCtx:

    url_args = {"q": ""}


def test_search_links(app, service, identity_simple, example_data, es_clear):
    """Test record links creation."""
    # Create a dummy record
    item = service.create(identity_simple, example_data)

    resource_requestctx = MockResourceRequestCtx()
    links_config = {
        "record": VocabularyLinksSchema,
        "search": SearchLinksSchema
    }
    result_list = service.search(
        identity=identity_simple,
        params=resource_requestctx.url_args,
        links_config=links_config,
    ).to_dict()

    expected_search_links = {
        "self": "https://localhost:5000/api/vocabularies/"
                "?page=1&q=&size=25&sort=newest"
    }

    assert result_list["links"] == expected_search_links

    expected_item_links = {
        "self": "/api/vocabularies/languages/{}".format(item._record.pid)
    }

    for hit in result_list["hits"]["hits"]:
        assert hit["links"] == expected_item_links
