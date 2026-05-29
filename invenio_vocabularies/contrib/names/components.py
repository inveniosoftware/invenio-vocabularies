# SPDX-FileCopyrightText: 2024 CERN.
# SPDX-License-Identifier: MIT

"""Names service components."""

from invenio_records_resources.services.records.components import ServiceComponent


class InternalIDComponent(ServiceComponent):
    """Service component for internal id field."""

    field = "internal_id"

    def create(self, identity, data=None, record=None, **kwargs):
        """Create handler."""
        setattr(record, self.field, data.pop(self.field, None))

    def update(self, identity, data=None, record=None, **kwargs):
        """Update handler."""
        setattr(record, self.field, data.pop(self.field, None))
