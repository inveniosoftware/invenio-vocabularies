# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from invenio_records_resources.proxies import current_service_registry


@pytest.fixture(scope="function")
def subject_full_data():
    """Controlled vocabulary backed subject data."""
    return {
        "title": {
            "en": "Dark Web",
            "de": "Darknet",
            "fr": "Réseaux anonymes (informatique)",
        },
        "subject": "Darknet",
        "id": "http://d-nb.info/gnd/1062531973",
        "scheme": "GND",
        "synonyms": ["Deep Web"],
    }


@pytest.fixture(scope="function")
def expected_subject_full_data():
    """Controlled vocabulary backed subject data."""
    return {
        "title": {
            "en": "Dark Web",
            "de": "Darknet",
            "fr": "Réseaux anonymes (informatique)",
        },
        "subject": "Darknet",
        "id": "http://d-nb.info/gnd/1062531973",
        "scheme": "GND",
        "synonyms": ["Deep Web"],
    }


@pytest.fixture(scope="module")
def service():
    """Subjects service object."""
    return current_service_registry.get("subjects")
