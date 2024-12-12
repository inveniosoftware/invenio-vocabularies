# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test alembic recipes for Invenio-Vocabularies."""

import pytest
from invenio_db.utils import drop_alembic_version_table


def assert_alembic(alembic, table_excludes, db):
    """Assert that metadata of alembic and db matches.

    This method allows omitting tables dynamically created for tests.
    """
    # We exclude assert checks in case we test mysql backend as there is an error
    # with mock_metadata table not being created i.e results to a "NoSuchTable()"
    # error when `alembic.compare_metadata()` runs
    if is_mysql_engine(db):
        return
    assert not list(
        filter(
            # x[0] is the operation and x[1] is the table
            lambda x: x[0] == "add_table" and x[1].name not in table_excludes,
            alembic.compare_metadata(),
        )
    )


def is_mysql_engine(db):
    """Helper function to return if mysql engine is the db backend."""
    return db.engine.name == "mysql"


def test_alembic(app, database):
    """Test alembic recipes."""
    db = database
    ext = app.extensions["invenio-db"]

    if db.engine.name == "sqlite":
        raise pytest.skip("Upgrades are not supported on SQLite.")

    # Check that this package's SQLAlchemy models have been properly registered
    tables = [x for x in db.metadata.tables]
    assert "vocabularies_metadata" in tables
    assert "vocabularies_types" in tables
    assert "vocabularies_schemes" in tables

    # Specific vocabularies models
    assert "subject_metadata" in tables
    assert "affiliation_metadata" in tables
    assert "name_metadata" in tables
    assert "funder_metadata" in tables
    assert "award_metadata" in tables

    # Check that Alembic agrees that there's no further tables to create.
    assert_alembic(ext.alembic, ["mock_metadata"], db)

    # Drop everything and recreate tables all with Alembic
    db.drop_all()
    drop_alembic_version_table()
    ext.alembic.upgrade()
    assert_alembic(ext.alembic, ["mock_metadata"], db)

    # Try to upgrade and downgrade
    ext.alembic.stamp()
    ext.alembic.downgrade(target="96e796392533")
    ext.alembic.upgrade()
    assert_alembic(ext.alembic, ["mock_metadata"], db)

    # Cleanup
    drop_alembic_version_table()
