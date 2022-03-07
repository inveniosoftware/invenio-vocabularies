#
# This file is part of Invenio.
# Copyright (C) 2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create funders table."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3d362de4926a'
down_revision = '8ff82dfb0be8'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.create_table(
        'funder_metadata',
        sa.Column(
            'created',
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'updated',
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'id',
            postgresql.UUID(),
            autoincrement=False,
            nullable=False),
        sa.Column(
            'json',
            postgresql.JSONB(astext_type=sa.Text()),
            autoincrement=False,
            nullable=True),
        sa.Column(
            'version_id',
            sa.INTEGER(),
            autoincrement=False,
            nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_funder_metadata')
    )


def downgrade():
    """Downgrade database."""
    op.drop_table('funder_metadata')
