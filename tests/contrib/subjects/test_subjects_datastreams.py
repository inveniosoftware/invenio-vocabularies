from unittest.mock import mock_open, patch

import pytest

from invenio_vocabularies.contrib.subjects.datastreams import (
    SubjectsYAMLReader,
    SubjectsYAMLTransformer,
)
from invenio_vocabularies.datastreams import StreamEntry


@pytest.fixture(scope="module")
def dict_subject_entry():
    return StreamEntry(
        {
            "subject": "Test Subject",
            "id": "123",
            "scheme": "Test Scheme",
        },
    )


def test_transformer(dict_subject_entry):
    transformer = SubjectsYAMLTransformer()

    transformed_entry = transformer.apply(dict_subject_entry)

    assert transformed_entry == {
        "subject": "Test Subject",
        "id": "123",
        "scheme": "Test Scheme",
    }
