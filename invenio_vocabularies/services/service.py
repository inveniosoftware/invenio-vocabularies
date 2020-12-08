# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Example service."""

from invenio_records_resources.services import RecordService, \
    RecordServiceConfig
from invenio_records_resources.services.records.search import terms_filter

from ..records.api import Vocabulary
from .components import VocabularyTypeComponent
from .permissions import PermissionPolicy
from .schema import VocabularySchema


class VocabulariesServiceConfig(RecordServiceConfig):
    """Mock service configuration."""

    permission_policy_cls = PermissionPolicy
    record_cls = Vocabulary
    schema = VocabularySchema
    search_facets_options = {
        "aggs": {
            "vocabulary_type": {
                "terms": {"field": "vocabulary_type"},
            }
        },
        "post_filters": {
            "vocabulary_type": terms_filter("vocabulary_type"),
        },
    }

    components = RecordServiceConfig.components + [
        VocabularyTypeComponent,
    ]


class VocabulariesService(RecordService):
    """Mock service."""

    default_config = VocabulariesServiceConfig
