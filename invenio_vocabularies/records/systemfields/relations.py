# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Relations system fields."""

from flask import current_app
from werkzeug.local import LocalProxy
from invenio_records.systemfields import RelationsField

from ..api import Vocabulary


class CustomFieldsRelation(RelationsField):
    """Relation field to manage custom fields."""

    def __init__(self, fields_var):
        """Initialize the field."""
        super().__init__()
        self._fields_var = fields_var
        self._fields = LocalProxy(lambda: self._load_custom_fields_relations())

    def _load_custom_fields_relations(self):
        cfs = current_app.config.get(self._fields_var, {})

        relations = {}
        for cf in cfs.values():
            if cf.relation_cls:
                relations[cf.name] = cf.relation_cls(
                    f"custom.{cf.name}",
                    keys=["title", "props", "icon"],
                    pid_field=Vocabulary.pid.with_type_ctx(cf.vocabulary_id),
                    cache_key=cf.vocabulary_id,
                )

        return relations

    def __set__(self, instance, values):
        """Setting the attribute."""
        raise ValueError("Cannot set this field directly.")
