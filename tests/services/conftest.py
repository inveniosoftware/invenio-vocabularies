# SPDX-FileCopyrightText: 2020-2021 CERN.
# SPDX-License-Identifier: MIT

"""Vocabularies test config."""

import pytest
from invenio_indexer.api import RecordIndexer

from invenio_vocabularies.records.api import Vocabulary


@pytest.fixture()
def indexer():
    """Indexer instance with correct Record class."""
    return RecordIndexer(
        record_cls=Vocabulary,
        record_to_index=lambda r: (r._record.index._name, "_doc"),
    )
