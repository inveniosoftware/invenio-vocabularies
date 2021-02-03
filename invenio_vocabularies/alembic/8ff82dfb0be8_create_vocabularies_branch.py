# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2021 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
