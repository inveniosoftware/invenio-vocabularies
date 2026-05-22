# SPDX-FileCopyrightText: 2016-2018 CERN.
# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Alter datetime columns to utc aware datetime columns."""

from invenio_db.utils import (
    update_table_columns_column_type_to_datetime,
    update_table_columns_column_type_to_utc_datetime,
)

# revision identifiers, used by Alembic.
revision = "d00af88aac94"
down_revision = "af2457652217"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    for table_name in [
        "vocabularies_metadata",
        "affiliation_metadata",
        "award_metadata",
        "subject_metadata",
        "name_metadata",
        "funder_metadata",
    ]:
        update_table_columns_column_type_to_utc_datetime(table_name, "created")
        update_table_columns_column_type_to_utc_datetime(table_name, "updated")


def downgrade():
    """Downgrade database."""
    for table_name in [
        "vocabularies_metadata",
        "affiliation_metadata",
        "award_metadata",
        "subject_metadata",
        "name_metadata",
        "funder_metadata",
    ]:
        update_table_columns_column_type_to_datetime(table_name, "created")
        update_table_columns_column_type_to_datetime(table_name, "updated")
