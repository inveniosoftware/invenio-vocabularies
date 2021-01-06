# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary resource."""

from flask import g
from flask_resources.context import resource_requestctx
from invenio_records_resources.resources import RecordResource, \
    RecordResourceConfig


class VocabulariesResourceConfig(RecordResourceConfig):
    """Custom record resource configuration."""

    list_route = "/vocabularies/<vocabulary_type>"
    item_route = f"{list_route}/<pid_value>"

    links_config = {}


class VocabulariesResource(RecordResource):
    """Custom record resource"."""

    default_config = VocabulariesResourceConfig

    def search(self):
        """Perform a search over the items."""
        identity = g.identity
        params = resource_requestctx.url_args

        # Pass the vocabulary_type in params so we can apply a post_filter
        # on it
        params.update(
            {
                "vocabulary_type": resource_requestctx.route[
                    "vocabulary_type"
                ],
            }
        )
        hits = self.service.search(
            identity=identity,
            params=params,
            links_config=self.config.links_config,
            es_preference=self._get_es_preference(),
        )
        return hits.to_dict(), 200
