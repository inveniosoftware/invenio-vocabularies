#
# This file is part of Invenio.
# Copyright (C) 2023 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Add "pid" column to names and affiliations tables."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "55a700f897b6"
down_revision = "e1146238edd3"
branch_labels = ()
depends_on = "999c62899c20"


pids_table = sa.sql.table(
    "pidstore_pid",
    sa.sql.column("pid_type"),
    sa.sql.column("pid_value"),
    sa.sql.column("object_uuid"),
    sa.sql.column("object_type"),
)
names_table = sa.sql.table(
    "name_metadata",
    sa.sql.column("id"),
    sa.sql.column("pid"),
)
affiliations_table = sa.sql.table(
    "affiliation_metadata",
    sa.sql.column("id"),
    sa.sql.column("pid"),
)


def upgrade():
    """Upgrade database."""
    op.add_column(
        "name_metadata",
        sa.Column("pid", sa.String(255), nullable=True),
    )
    # populate from PIDStore
    op.execute(
        names_table.update()
        .where(
            names_table.c.id == pids_table.c.object_uuid,
            pids_table.c.object_type == "rec",
            pids_table.c.pid_type == "names",
        )
        .values(pid=pids_table.c.pid_value)
    )
    op.create_unique_constraint(
        op.f("uq_name_metadata_pid"),
        "name_metadata",
        ["pid"],
    )

    op.add_column(
        "affiliation_metadata",
        sa.Column("pid", sa.String(255), nullable=True),
    )
    # populate from PIDStore
    op.execute(
        affiliations_table.update()
        .where(
            affiliations_table.c.id == pids_table.c.object_uuid,
            pids_table.c.object_type == "rec",
            pids_table.c.pid_type == "aff",
        )
        .values(pid=pids_table.c.pid_value)
    )

    op.create_unique_constraint(
        op.f("uq_affiliation_metadata_pid"),
        "affiliation_metadata",
        ["pid"],
    )


def downgrade():
    """Downgrade database."""
    op.drop_constraint(
        op.f("uq_name_metadata_pid"),
        "name_metadata",
        type_="unique",
    )
    op.drop_constraint(
        op.f("uq_affiliation_metadata_pid"),
        "affiliation_metadata",
        type_="unique",
    )
    op.drop_column("name_metadata", "pid")
    op.drop_column("affiliation_metadata", "pid")
