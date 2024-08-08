# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 University of Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Subject datastream tests."""
import logging
from pathlib import Path

import idutils
import pytest

from invenio_vocabularies.datastreams import StreamEntry
from invenio_vocabularies.datastreams.readers import YamlReader

subject_schemes = {
    "gnd": {"label": "GND", "validator": idutils.is_gnd, "datacite": "GND"},
}


@pytest.fixture(scope="module")
def subject_as_yaml():
    subject = """
        - subject:
              en: Dark Web
              de: Darknet
              fr: Réseaux anonymes (informatique)
          id: "http://d-nb.info/gnd/1062531973"
          scheme: GND
          synonyms:
          - Deep Web
    """
    return subject


@pytest.fixture(scope="function")
def yaml_file(subject_as_yaml):
    filename = Path("reader_test.yaml")
    with open(filename, "w") as file:
        file.write(subject_as_yaml)

    yield filename

    filename.unlink()  # delete created file


@pytest.fixture(scope="module")
def dict_subject_entry():
    return StreamEntry(
        {
            "title": {
                "en": "Dark Web",
                "de": "Darknet",
                "fr": "Réseaux anonymes (informatique)",
            },
            "id": "http://d-nb.info/gnd/1062531973",
            "scheme": "GND",
            "synonyms": ["Deep Web"],
        },
    )
