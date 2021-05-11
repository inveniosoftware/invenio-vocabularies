# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""System field context for the Vocabulary PID field.

The context overrides the PID resolver to be aware of the vocabulary type, and
hence the PID type.

The context is used when you initialise a PIField, for instance:

.. code-block:: python

    class Vocabulary(Record):
        pid = PIDField(
            'id',
            provider=VocabularyIdProvider,
            context_cls=VocabularyPIDFieldContext
        )

You can then resolve vocabulary records using the type:

.. code-block:: python

    Vocabulary.pid.resolve(('<type>', '<pid_value>'))


Also, it's possible to make initialise the field with a type context:

.. code-block:: python

    Vocabulary.pid.with_type_ctx('<type>').resolve('<pid_value>')

"""

from copy import copy

from invenio_db import db
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records.systemfields import RelatedModelFieldContext

from invenio_vocabularies.records.models import VocabularyType


class VocabularyPIDFieldContext(RelatedModelFieldContext):
    """PIDField context for vocabularies.

    This class implements the class-level methods available on a PIDField
    for vocabulary records.
    """

    def create(self, record):
        """Proxy to the field's create method."""
        return self.field.create(record)

    def delete(self, record):
        """Proxy to the field's delete method."""
        return self.field.delete(record)

    def resolve(self, pid_value):
        """Resolve identifier.

        :params pid_value: Either a tuple ``(type_id, pid_value)`` or just a
            ``pid_value`` if the type context has been initialized using
            ``with_type_ctx()``.
        """
        pid_type = self.pid_type
        if pid_type is None:
            type_id, pid_value = pid_value
            pid_type = self.get_pid_type(type_id)

        # Create resolver
        resolver = self.field._resolver_cls(
            pid_type=pid_type,
            object_type=self.field._object_type,
            getter=self.record_cls.get_record
        )

        # Resolve
        pid, record = resolver.resolve(pid_value)

        # Store pid in cache on record.
        self.field._set_cache(record, pid)

        return record

    def get_pid_type(self, type_id):
        """Get the PID type for a vocabulary type."""
        # Get type based on name.
        vocab_type = VocabularyType.query.filter_by(id=type_id).one_or_none()
        if vocab_type is None:
            raise PIDDoesNotExistError(None, None)
        return vocab_type.pid_type

    @property
    def pid_type(self):
        """Get the current defined type."""
        # This ensures that when we use Vocabulary.pid.with_type_ctx('...')
        # we cache the pid type to avoid querying the database every time.
        type_id = getattr(self, '_type_id', None)
        if type_id:
            pid_type = getattr(self, '_pid_type', None)
            if pid_type is None:
                pid_type = self.get_pid_type(type_id)
                self._pid_type = pid_type
            return pid_type

    def with_type_ctx(self, type_id):
        """Returns a new context initialized with the type context."""
        ctx = copy(self)
        ctx._type_id = type_id
        return ctx
