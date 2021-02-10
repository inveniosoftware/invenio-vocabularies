# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabularies test config."""

import pytest
from flask_principal import Identity
from invenio_access.permissions import any_user, system_process
from invenio_indexer.api import RecordIndexer

from invenio_vocabularies.records.api import Vocabulary


@pytest.fixture()
def identity():
    """Simple identity to interact with the service."""
    identity = Identity(1)
    identity.provides.add(any_user)
    identity.provides.add(system_process)
    return identity


@pytest.fixture()
def indexer():
    """Indexer instance with correct Record class."""
    return RecordIndexer(
        record_cls=Vocabulary,
        record_to_index=lambda r: (r._record.index._name, "_doc"),
    )
