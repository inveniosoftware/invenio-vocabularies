#
# This file is part of Invenio.
# Copyright (C) 2024 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Add internal name ID."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "3ba812d80559"
down_revision = "55a700f897b6"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.add_column(
        "name_metadata", sa.Column("internal_id", sa.String(length=255), nullable=True)
    )
    op.create_unique_constraint(
        op.f("uq_name_metadata_internal_id"), "name_metadata", ["internal_id"]
    )


def downgrade():
    """Downgrade database."""
    op.drop_constraint(
        op.f("uq_name_metadata_internal_id"), "name_metadata", type_="unique"
    )
    op.drop_column("name_metadata", "internal_id")
