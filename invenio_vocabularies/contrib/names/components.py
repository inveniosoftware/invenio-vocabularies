#
# This file is part of Invenio.
# Copyright (C) 2024 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
