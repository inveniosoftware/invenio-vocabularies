# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the vocabulary service facets."""

import pytest
from flask_babelex import lazy_gettext as _
from invenio_access.permissions import system_identity

from invenio_vocabularies.proxies import current_service
from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.services.facets import NestedVocabularyTermsFacet, \
    VocabularyLabels
from invenio_vocabularies.services.facets.facets import LabellingBucket


class DummyData:
    """Dummy data with buckets."""
    buckets = [
        LabellingBucket("rootone", 2),
        LabellingBucket("rootone-subone", 1),
        LabellingBucket("rootone-subone-subone", 4),
        LabellingBucket("rootone-subtwo", 3),
        LabellingBucket("roottwo", 5)
    ]


def test_nested_vocabulary_facet_labelling(app):
    # create vocabulary type
    current_service.create_type(system_identity, "nested_vocab", "nes")

    # add vocabulary items
    current_service.create(system_identity, {
        "id": "rootone",
        "props": {
            "type": "rootone",
            "type_name": "rootone",
        },
        "title": {
            "en": "Root One"
        },
        "type": "nested_vocab"
    })

    current_service.create(system_identity, {
        "id": "rootone-subone",
        "props": {
            "type": "rootone-subone",
            "type_name": "rootone-subone",
        },
        "title": {
            "en": "Root One Sub One"
        },
        "type": "nested_vocab"
    })

    current_service.create(system_identity, {
        "id": "rootone-subtwo",
        "props": {
            "type": "rootone-subtwo",
            "type_name": "rootone-subtwo",
        },
        "title": {
            "en": "Root One Sub Two"
        },
        "type": "nested_vocab"
    })

    current_service.create(system_identity, {
        "id": "rootone-subone-subone",
        "props": {
            "type": "rootone-subone-subone",
            "type_name": "rootone-subone-subone",
        },
        "title": {
            "en": "Root One Sub Sub One"
        },
        "type": "nested_vocab"
    })

    current_service.create(system_identity, {
        "id": "roottwo",
        "props": {
            "type": "roottwo",
            "type_name": "roottwo",
        },
        "title": {
            "en": "Root Two"
        },
        "type": "nested_vocab"
    })

    Vocabulary.index.refresh()

    # expected data
    nested_item_labels = {'buckets': [
        {
            'key': 'rootone',
            'doc_count': 10,  # 2 + 1 + 4 + 3
            'label': _('Root One'),
            'is_selected': False,
            'inner': {'buckets': [
                {
                    'key': 'rootone-subone',
                    'doc_count': 5,  # 1 + 4
                    'label': _('Root One Sub One'),
                    'is_selected': False,
                    'inner': {'buckets': [
                        {
                            'key': 'rootone-subone-subone',
                            'doc_count': 4,
                            'label': _('Root One Sub Sub One'),
                            'is_selected': False
                        }
                    ]}
                }, {
                    'key': 'rootone-subtwo',
                    'doc_count': 3,
                    'label': _('Root One Sub Two'),
                    'is_selected': False
                }
            ]}
        }, {
            'key': 'roottwo',
            'doc_count': 5,
            'label': _('Root Two'),
            'is_selected': False
        }],
        'label': 'Nested Aggs'
    }

    nested_buckets = DummyData()

    # the test
    resource_type_facet = NestedVocabularyTermsFacet(
        field='dummy.not.used',
        label=_("Nested Aggs"),
        value_labels=VocabularyLabels('nested_vocab')
    )

    aggs_labels = resource_type_facet.get_labelled_values(
        data=nested_buckets, filter_values=())

    assert nested_item_labels == aggs_labels


def test_nested_vocabulary_facet_labelling_empty_agg(app):
    # expected data
    nested_item_labels = {
        'buckets': [],
        'label': 'Nested Aggs'
    }

    resource_type_facet = NestedVocabularyTermsFacet(
        field='dummy.not.used',
        label=_("Nested Aggs"),
        value_labels=VocabularyLabels('nested_vocab')
    )

    data = DummyData()
    data.buckets = []

    aggs_labels = resource_type_facet.get_labelled_values(
        data=data, filter_values=())

    assert nested_item_labels == aggs_labels
