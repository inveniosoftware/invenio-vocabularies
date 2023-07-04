# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Relations system fields."""

from flask import current_app
from invenio_records.systemfields import RelationsField
from werkzeug.utils import cached_property

from ..api import Vocabulary


class CustomFieldsRelation(RelationsField):
    """Relation field to manage custom fields.

    Iterates through all configured custom fields and collects the ones
    defining a relation dependency e.g vocabularies.
    """

    def __init__(self, fields_var):
        """Initialize the field."""
        super().__init__()
        self._fields_var = fields_var

    @cached_property
    def _fields(self):
        """Loads custom fields relations from config."""
        custom_fields = current_app.config.get(self._fields_var, {})

        relations = {}
        for cf in custom_fields:
            if getattr(cf, "relation_cls", None):
                relations[cf.name] = cf.relation_cls(
                    f"custom_fields.{cf.name}",
                    keys=cf.field_keys,
                    pid_field=Vocabulary.pid.with_type_ctx(cf.vocabulary_id),
                    cache_key=cf.vocabulary_id,
                )

        return relations

    def __set__(self, instance, values):
        """Setting the attribute."""
        raise ValueError(
            f"This field can only be set through config ({self._fields_var})"
        )
