# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Resources layer tests."""

from flask_babelex import Babel


def test_endpoint_localization(app, client, example_record, monkeypatch):
    """Test that the endpoint returns the correct translation."""

    # monkeypatch.setattr(
    #     "flask_babelex.get_locale", lambda: Babel().load_locale("fr")
    # )
    res = client.get(
        "/vocabularies/languages", headers={"accept": "application/json"}
    )
    assert res.status_code == 200
    es_record = res.json["hits"]["hits"][0]
    assert es_record["metadata"]["title"]["fr"] == "Titre test"
