# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create vocabularies tables."""

import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op
from sqlalchemy.dialects import mysql, postgresql

# revision identifiers, used by Alembic.
revision = "4f365fced43f"
down_revision = "8ff82dfb0be8"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.create_table(
        "subject_metadata",
        sa.Column(
            "created",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
                "postgresql",
            )
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "sqlite"),
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subject_metadata")),
    )
    op.create_table(
        "vocabularies_metadata",
        sa.Column(
            "created",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
                "postgresql",
            )
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "sqlite"),
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_vocabularies_metadata")),
    )
    op.create_table(
        "vocabularies_types",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("pid_type", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_vocabularies_types")),
        sa.UniqueConstraint("pid_type", name=op.f("uq_vocabularies_types_pid_type")),
    )


def downgrade():
    """Downgrade database."""
    op.drop_table("vocabularies_types")
    op.drop_table("vocabularies_metadata")
    op.drop_table("subject_metadata")
