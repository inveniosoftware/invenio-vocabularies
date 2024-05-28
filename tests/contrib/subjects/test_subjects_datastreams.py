from unittest.mock import mock_open, patch

import pytest

from invenio_vocabularies.contrib.subjects.datastreams import (
    SubjectsYAMLReader,
    SubjectsYAMLTransformer,
)
from invenio_vocabularies.datastreams import StreamEntry


def test_read():
    # Arrange
    mock_yaml_data = [
        [
            {
                "id": "http://www.oecd.org/science/inno/38235147.pdf?6.5",
                "scheme": "FOS",
                "subject": "Other humanities",
            }
        ]
    ]
    reader = SubjectsYAMLReader(options={"filename": "subjects.yaml"})

    with patch(
        "builtins.open",
        mock_open(
            read_data='- id: "http://www.oecd.org/science/inno/38235147.pdf?6.5"\\n  scheme: FOS\\n  subject: "Other humanities"'
        ),
    ) as m:
        with patch("yaml.safe_load", return_value=mock_yaml_data) as mock_yaml:

            data = list(reader.read())  # Convert the generator to a list to consume it

            m.assert_called_once_with("subjects.yaml", "r")
            mock_yaml.assert_called_once()

            assert (
                data == mock_yaml_data
            )  # Check that the data returned by read is correct


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
