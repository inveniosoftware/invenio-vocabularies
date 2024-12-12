#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Drop unique constraint from internal id."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "af2457652217"
down_revision = "3ba812d80559"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.drop_constraint("uq_name_metadata_internal_id", "name_metadata", type_="unique")
    op.create_index(
        op.f("ix_name_metadata_internal_id"),
        "name_metadata",
        ["internal_id"],
        unique=False,
    )


def downgrade():
    """Downgrade database."""
    op.drop_index(op.f("ix_name_metadata_internal_id"), table_name="name_metadata")
    op.create_unique_constraint(
        "uq_name_metadata_internal_id", "name_metadata", ["internal_id"]
    )
