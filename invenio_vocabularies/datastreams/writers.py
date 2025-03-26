# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Writers module."""

from abc import ABC, abstractmethod
from pathlib import Path

import yaml
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDAlreadyExists, PIDDoesNotExistError
from invenio_records.systemfields.relations.errors import InvalidRelationValue
from invenio_records_resources.proxies import current_service_registry
from marshmallow import ValidationError
from sqlalchemy.exc import NoResultFound

from .datastreams import StreamEntry
from .errors import WriterError
from .tasks import write_entry, write_many_entry


class BaseWriter(ABC):
    """Base writer."""

    def __init__(self, *args, **kwargs):
        """Base initialization logic."""
        # Add any base initialization here if needed
        pass

    @abstractmethod
    def write(self, stream_entry, *args, **kwargs):
        """Writes the input stream entry to the target output.

        :returns: A StreamEntry. The result of writing the entry.
                  Raises WriterException in case of errors.

        """
        pass

    @abstractmethod
    def write_many(self, stream_entries, *args, **kwargs):
        """Writes the input streams entry to the target output.

        :returns: A List of StreamEntry. The result of writing the entry.
                  Raises WriterException in case of errors.

        """
        pass


class ServiceWriter(BaseWriter):
    """Writes the entries to an RDM instance using a Service object."""

    def __init__(
        self, service_or_name, *args, identity=None, insert=True, update=False, **kwargs
    ):
        """Constructor.

        :param service_or_name: a service instance or a key of the
                                service registry.
        :param identity: access identity.
        :param insert: if True it will insert records which do not exist.
        :param update: if True it will update records if they exist.
        """
        if isinstance(service_or_name, str):
            service_or_name = current_service_registry.get(service_or_name)

        self._service = service_or_name
        self._identity = identity or system_identity
        self._insert = insert
        self._update = update

        super().__init__(*args, **kwargs)

    def _entry_id(self, entry):
        """Get the id from an entry."""
        return (entry["type"], entry["id"])

    def _resolve(self, id_):
        return self._service.read(self._identity, id_)

    def _do_update(self, entry):
        vocab_id = self._entry_id(entry)
        current_app.logger.debug(f"Resolving entry with ID: {vocab_id}")
        current = self._resolve(vocab_id)
        updated = dict(current.to_dict(), **entry)
        current_app.logger.debug(f"Updating entry with ID: {vocab_id}")
        return StreamEntry(self._service.update(self._identity, vocab_id, updated))

    def write(self, stream_entry, *args, **kwargs):
        """Writes the input entry using a given service."""
        entry = stream_entry.entry
        current_app.logger.debug(f"Writing entry: {entry}")

        try:
            if self._insert:
                try:
                    current_app.logger.debug("Inserting entry.")
                    return StreamEntry(self._service.create(self._identity, entry))
                except PIDAlreadyExists:
                    if not self._update:
                        raise WriterError([f"Vocabulary entry already exists: {entry}"])
                    return self._do_update(entry)
            elif self._update:
                try:
                    current_app.logger.debug("Attempting to update entry.")
                    return self._do_update(entry)
                except (NoResultFound, PIDDoesNotExistError):
                    raise WriterError([f"Vocabulary entry does not exist: {entry}"])
            else:
                raise WriterError(
                    ["Writer wrongly configured to not insert and to not update"]
                )

        except ValidationError as err:
            raise WriterError([{"ValidationError": err.messages}])
        except InvalidRelationValue as err:
            # TODO: Check if we can get the error message easier
            raise WriterError([{"InvalidRelationValue": err.args[0]}])

    def write_many(self, stream_entries, *args, **kwargs):
        """Writes the input entries using a given service."""
        current_app.logger.info(f"Writing {len(stream_entries)} entries")
        entries = [entry.entry for entry in stream_entries]
        entries_with_id = [(self._entry_id(entry), entry) for entry in entries]
        result_list = self._service.create_or_update_many(
            self._identity, entries_with_id
        )
        stream_entries_processed = []
        for entry, result in zip(entries, result_list.results):
            processed_stream_entry = StreamEntry(
                entry=entry,
                record=result.record,
                errors=result.errors,
                op_type=result.op_type,
                exc=result.exc,
            )
            processed_stream_entry.log_errors()
            stream_entries_processed.append(processed_stream_entry)

        current_app.logger.debug(f"Finished writing {len(stream_entries)} entries")
        return stream_entries_processed


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
            yaml.safe_dump([stream_entry.entry], file, allow_unicode=True)

        return stream_entry

    def write_many(self, stream_entries, *args, **kwargs):
        """Writes the yaml input entries."""
        with open(self._filepath, "a") as file:
            yaml.safe_dump(
                [stream_entry.entry for stream_entry in stream_entries],
                file,
                allow_unicode=True,
            )


class AsyncWriter(BaseWriter):
    """Writes the entries asynchronously (celery task)."""

    def __init__(self, writer, *args, **kwargs):
        """Constructor.

        :param writer: writer to use.
        """
        super().__init__(*args, **kwargs)
        self._writer = writer

    def write(self, stream_entry, *args, **kwargs):
        """Launches a celery task to write an entry."""
        write_entry.delay(self._writer, stream_entry.entry)

        return stream_entry

    def write_many(self, stream_entries, *args, **kwargs):
        """Launches a celery task to write an entry."""
        write_many_entry.delay(
            self._writer, [stream_entry.entry for stream_entry in stream_entries]
        )

        return stream_entries
