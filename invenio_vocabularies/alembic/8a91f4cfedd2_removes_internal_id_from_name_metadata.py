#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Removes internal_id from name_metadata."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "8a91f4cfedd2"
down_revision = "af2457652217"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.drop_index("ix_name_metadata_internal_id", table_name="name_metadata")
    op.drop_column("name_metadata", "internal_id")


def downgrade():
    """Downgrade database."""
    op.add_column(
        "name_metadata",
        sa.Column(
            "internal_id", sa.VARCHAR(length=255), autoincrement=False, nullable=True
        ),
    )
    op.create_index(
        "ix_name_metadata_internal_id", "name_metadata", ["internal_id"], unique=False
    )
