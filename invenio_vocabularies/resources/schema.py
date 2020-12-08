# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary links schemas."""

from invenio_records_resources.resources import search_link_params, \
    search_link_when
from marshmallow import Schema
from marshmallow_utils.fields import Link
from uritemplate import URITemplate

# TODO: See how much can be reused from Invenio-Records-Resources


def vocabularies_search_link_params(page_offset):
    """Params function factory."""

    def _inner(search_dict):
        # Filter out internal parameters
        params = {
            k: v for k, v in search_dict.items() if not k.startswith("_")
        }
        params["page"] += page_offset
        vocabulary_type = params.get("vocabulary_type")
        return {"params": params, "vocabulary_type": vocabulary_type}

    return _inner


class VocabularyLinksSchema(Schema):
    """Schema for a record's links."""

    # NOTE:
    #   - /api prefix is needed here because above are mounted on /api
    self = Link(
        template=URITemplate(
            "/api/vocabularies/{vocabulary_type}/{pid_value}"
        ),
        permission="read",
        params=lambda record: {
            "pid_value": record.pid.pid_value,
            "vocabulary_type":
                record.vocabulary_type or record.get('vocabulary_type')
        },
        data_key="self",  # To avoid using self since is python reserved key
    )


class SearchLinksSchema(Schema):
    """Schema for a search result's links."""

    # NOTE:
    #   - /api prefix is needed here because api routes are mounted on /api

    self = Link(
        template=URITemplate("/api/vocabularies/{vocabulary_type}{?params*}"),
        permission="search",
        params=vocabularies_search_link_params(0),
    )
    prev = Link(
        template=URITemplate("/api/vocabularies/{vocabulary_type}{?params*}"),
        permission="search",
        params=vocabularies_search_link_params(-1),
        when=search_link_when(-1),
    )
    next = Link(
        template=URITemplate("/api/vocabularies/{vocabulary_type}{?params*}"),
        permission="search",
        params=vocabularies_search_link_params(+1),
        when=search_link_when(+1),
    )
