# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary components."""

from invenio_i18n import lazy_gettext as _
from invenio_records_resources.services.records.components import ServiceComponent
from marshmallow import ValidationError
from sqlalchemy.orm.exc import NoResultFound

from ..records.models import VocabularyType


class VocabularyTypeComponent(ServiceComponent):
    """Set the record's vocabulary type."""

    def _set_type(self, data, record):
        type_id = data.pop("type", None)
        if type_id:
            try:
                record.type = VocabularyType.query.filter_by(id=type_id["id"]).one()
            except NoResultFound:
                raise ValidationError(
                    _("The vocabulary type does not exists."),
                    field_name="type",
                )

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject vocabulary type to the record."""
        self._set_type(data, record)

    def update(self, identity, data=None, record=None, **kwargs):
        """Inject vocabulary type to the record."""
        self._set_type(data, record)


class PIDComponent(ServiceComponent):
    """PID registration component."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Create PID when record is created.."""
        # We create the PID after all the data has been initialized. so that
        # we can rely on having the 'id' and type set.
        self.service.record_cls.pid.create(record)


class ModelPIDComponent(PIDComponent):
    """Model PID registration component."""

    def update(self, identity, data=None, record=None, **kwargs):
        """Update an existing record."""
        record.pop("pid", None)
        record.pop("id", None)
