#
# This file is part of Invenio.
# Copyright (C) 2021 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create names table."""

import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op
from sqlalchemy.dialects import mysql, postgresql

# revision identifiers, used by Alembic.
revision = "17c703ce1eb7"
down_revision = "4a9a4fd235f8"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.create_table(
        "name_metadata",
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
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "sqlite"),
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_name_metadata")),
    )


def downgrade():
    """Downgrade database."""
    op.drop_table("name_metadata")
