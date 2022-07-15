# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Writers module."""

from abc import ABC, abstractmethod
from pathlib import Path

import yaml
from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDAlreadyExists
from invenio_records.systemfields.relations.errors import InvalidRelationValue
from invenio_records_resources.proxies import current_service_registry
from marshmallow import ValidationError

from .datastreams import StreamEntry
from .errors import WriterError


class BaseWriter(ABC):
    """Base writer."""

    @abstractmethod
    def write(self, stream_entry, *args, **kwargs):
        """Writes the input stream entry to the target output.

        :returns: A StreamEntry. The result of writing the entry.
                  Raises WriterException in case of errors.

        """
        pass


class ServiceWriter(BaseWriter):
    """Writes the entries to an RDM instance using a Service object."""

    def __init__(self, service_or_name, *args, identity=None, update=False, **kwargs):
        """Constructor.

        :param service_or_name: a service instance or a key of the
                                service registry.
        :param identity: access identity.
        :param update: if True it will update records if they exist.
        """
        if isinstance(service_or_name, str):
            service_or_name = current_service_registry.get(service_or_name)

        self._service = service_or_name
        self._identity = identity or system_identity
        self._update = update

        super().__init__(*args, **kwargs)

    def _entry_id(self, entry):
        """Get the id from an entry."""
        return (entry["type"], entry["id"])

    def _resolve(self, id_):
        return self._service.read(self._identity, id_)

    def write(self, stream_entry, *args, **kwargs):
        """Writes the input entry using a given service."""
        entry = stream_entry.entry
        try:
            try:
                return StreamEntry(self._service.create(self._identity, entry))
            except PIDAlreadyExists:
                if not self._update:
                    raise WriterError([f"Vocabulary entry already exists: {entry}"])
                vocab_id = self._entry_id(entry)
                current = self._resolve(vocab_id)
                updated = dict(current.to_dict(), **entry)
                return StreamEntry(
                    self._service.update(self._identity, vocab_id, updated)
                )

        except ValidationError as err:
            raise WriterError([{"ValidationError": err.messages}])
        except InvalidRelationValue as err:
            # TODO: Check if we can get the error message easier
            raise WriterError([{"InvalidRelationValue": err.args[0]}])


class YamlWriter(BaseWriter):
    """Writes the entries to a YAML file."""

    def __init__(self, filepath, *args, **kwargs):
        """Constructor.

        :param filepath: path of the output file.
        """
        self._filepath = Path(filepath)

        super().__init__(*args, **kwargs)

    def write(self, stream_entry, *args, **kwargs):
        """Writes the input stream entry using a given service."""
        with open(self._filepath, "a") as file:
            # made into array for safer append
            # will always read array (good for reader)
            yaml.safe_dump([stream_entry.entry], file)

        return stream_entry
