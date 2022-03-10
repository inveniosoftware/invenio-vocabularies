# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
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
from invenio_records.systemfields import ModelField
from invenio_records_resources.records.systemfields.pid import PIDFieldContext

from ..models import VocabularyType
from ..pidprovider import FromFieldProvider
from ..resolvers import ModelResolver


class BaseVocabularyPIDFieldContext(PIDFieldContext):
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


class VocabularyPIDFieldContext(BaseVocabularyPIDFieldContext):
    """PIDField context for vocabularies.

    This class implements the class-level methods available on a PIDField
    for vocabulary records.
    """

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


class ModelPIDFieldContext(PIDFieldContext):
    """Context for ModelPIDField.

    This class implements the class-level methods available on a PIDField. I.e.
    when you access the field through the class, for instance:

    .. code-block:: python

        Record.pid.resolve('...')
        Record.pid.session_merge(record)
    """

    def resolve(self, pid_value, registered_only=True):
        """Resolve identifier."""
        resolver = self.field._resolver_cls(
            self._record_cls, self.field.model_field_name
        )
        pid, record = resolver.resolve(pid_value)
        self.field._set_cache(record, pid)

        return record

    def session_merge(self, record):
        """Inactivate session merge since it all belongs to the same db obj."""
        pass


class ModelPIDField(ModelField):
    """PID field in a db column on the record model. """

    def __init__(
        self,
        model_field_name="pid",
        provider=FromFieldProvider,
        resolver_cls=ModelResolver,
        context_cls=ModelPIDFieldContext,
    ):
        """Initialise the dict field.
        :param key: Name of key to store the pid value in.
        """
        self._provider = provider
        self._resolver_cls = resolver_cls
        self._context_cls = context_cls
        super().__init__(model_field_name=model_field_name)

    def create(self, record):
        """Method to create a new persistent identifier for the record."""
        # This uses the fields __get__() data descriptor method below
        pid = getattr(record, self.attr_name)
        if pid is None:
            # Set using the __set__() method
            pid_value = self._provider.create(record)
            setattr(record, self.attr_name, pid_value)
        return pid

    #
    # Data descriptor
    #
    def __get__(self, record, owner=None):
        """Accessing the attribute."""
        # Class access
        if record is None:
            return self._context_cls(self, owner)
        # Instance access
        try:
            return getattr(record.model, self.model_field_name)
        except AttributeError:
            return None
    #
    # Life-cycle hooks
    #

    def pre_create(self, record):
        """Called after a record is created."""
        self.create(record)
