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


def test_endpoint_read(app, client, example_record):
    """Test the endpoint to retrieve a single item."""
    res = client.get(
        "/vocabularies/languages/{}".format(example_record.id),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200
    assert res.json["id"] == example_record.id

    res = client.get(
        "/vocabularies/nonexistent/{}".format(example_record.id),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 200  # (!) current behavior, might change
    assert res.json["id"] == example_record.id

    res = client.get(
        "/vocabularies/languages/{}".format("nonexistent"),
        headers={"accept": "application/json"},
    )
    assert res.status_code == 404
