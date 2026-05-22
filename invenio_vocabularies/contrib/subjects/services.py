# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-FileCopyrightText: 2021 Northwestern University.
# SPDX-License-Identifier: MIT

"""Subjects services."""

from invenio_db import db

from ...records.models import VocabularyScheme
from .subjects import record_type

SubjectsServiceConfig = record_type.service_config_cls


class SubjectsService(record_type.service_cls):
    """Subjects service."""

    def create_scheme(self, identity, id_, name="", uri=""):
        """Create a row for the subject scheme metadata."""
        self.require_permission(identity, "manage")
        scheme = VocabularyScheme.create(
            id=id_, parent_id="subjects", name=name, uri=uri
        )
        db.session.commit()
        return scheme
