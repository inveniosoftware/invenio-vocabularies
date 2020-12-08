# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Constant system field."""

from invenio_records.systemfields import ModelField


class VocabularyTypeField(ModelField):
    """Model field for providing get and set access on a model field."""

    #
    # Data descriptor
    #
    def __get__(self, record, owner=None):
        """Accessing the attribute."""
        # Class access
        if record is None:
            return self
        # Instance access
        try:
            return getattr(record.model, self.model_field_name).name
        except AttributeError:
            return None

    def __set__(self, instance, value):
        """Accessing the attribute."""
        self._set(instance.model, value.name)

    #
    # Record extension
    #
    def post_init(self, record, data, model=None, field_data=None):
        """Initialise the model field."""
        if field_data is not None:
            self._set(model, field_data)
