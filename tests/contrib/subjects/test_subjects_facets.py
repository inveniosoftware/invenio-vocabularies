# SPDX-FileCopyrightText: 2021 Northwestern University.
# SPDX-License-Identifier: MIT

"""Test the subjects facets."""

from invenio_vocabularies.contrib.subjects import SubjectsLabels


def test_subjects_label_duplicates():
    labels_instance = SubjectsLabels()

    result = labels_instance(["MeSH", "MeSH"])

    assert {"MeSH": "MeSH"} == result

    result = labels_instance(["Abdomen", "Abdomen", "Abdomen"])

    assert {"Abdomen": "Abdomen"} == result


def test_subjects_label_empty():
    labels_instance = SubjectsLabels()

    result = labels_instance([])

    assert {} == result
