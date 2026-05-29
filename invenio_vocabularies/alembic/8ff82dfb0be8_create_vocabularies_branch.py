# SPDX-FileCopyrightText: 2021 TU Wien.
# SPDX-License-Identifier: MIT

"""Create vocabularies branch."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8ff82dfb0be8"
down_revision = None
branch_labels = ("invenio_vocabularies",)
depends_on = "dbdbc1b19cf2"


def upgrade():
    """Upgrade database."""
    pass


def downgrade():
    """Downgrade database."""
    pass
