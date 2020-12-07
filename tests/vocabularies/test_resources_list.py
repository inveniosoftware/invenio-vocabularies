# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Resources layer tests."""

from flask_babelex import Babel

from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.models import VocabularyType


def test_endpoint_list(app, db, client, example_record):
    """Test the list endpoint."""

    # existing vocabulary
    res = client.get(
        "/vocabularies/languages", headers={"accept": "application/json"}
    )
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1

    # nonexistent vocabulary
    res = client.get(
        "/vocabularies/nonexistent", headers={"accept": "application/json"}
    )
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 0


def test_endpoint_filter(app, db, client, identity, service):
    """Test the list endpoint while filtering by vocabulary type."""

    vocabulary_type_1 = VocabularyType(name="type1")
    db.session.add(vocabulary_type_1)
    vocabulary_type_2 = VocabularyType(name="type2")
    db.session.add(vocabulary_type_2)
    db.session.commit()

    record1 = service.create(
        identity=identity,
        data=dict(
            metadata=dict(id="id1"), vocabulary_type_id=vocabulary_type_1.id
        ),
    )
    record2 = service.create(
        identity=identity,
        data=dict(
            metadata=dict(id="id2"), vocabulary_type_id=vocabulary_type_2.id
        ),
    )

    Vocabulary.index.refresh()

    res = client.get(
        "/vocabularies/type1", headers={"accept": "application/json"}
    )
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 1
    assert res.json["hits"]["hits"][0]["id"] == record1.id
