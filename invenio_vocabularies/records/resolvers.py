# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Persistent identifier resolver for vocabularies."""

from invenio_db import db


class ModelResolver(object):
    """Resolver for records with an in-table PID.

    This resolver applies to custom records that do not store the PID in
    pidstore, but instead its value is stored in the same db table.
    """

    def __init__(self, record_cls, model_field_name, **kwargs):
        """Initialize resolver."""
        self._record_cls = record_cls
        self.model_field_name = model_field_name

    def resolve(self, pid_value):
        """Resolver that bypasses PIDStore.

        :param pid_value: string.
        :returns: A tuple containing (pid, object).
        """
        with db.session.no_autoflush:  # avoid flushing the current session
            filters = {self.model_field_name: pid_value}
            query = self._record_cls.model_cls.query.filter_by(**filters)
            obj = query.one()
            return (
                pid_value,
                self._record_cls(obj.data, model=obj)
            )
