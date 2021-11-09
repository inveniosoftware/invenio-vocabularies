# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Writers module."""

from .errors import WriterError


class BaseWriter:
    """Base writer."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        pass

    def write(self, entry, *args, **kwargs):
        """Writes the input entry to the target output.

        Raises WriterException in case of errors.
        """
        pass


class ServiceWriter(BaseWriter):
    """Writes the entries to an RDM instance using a Service object."""

    def __init__(self, service, identity, *args, **kwargs):
        """Constructor."""
        self._service = service
        self._identity = identity

    def write(self, entry, *args, **kwargs):
        """Writes the input entry using a given service."""
        result = self._service.create(entry, identity=self._identity)
        if result.errors:
            raise WriterError(result.errors)


class FileWriter(BaseWriter):
    """File writer."""

    def __init__(self, filepath, *args, **kwargs):
        """Constructor."""
        self._filepath = filepath

    def write(self, entry, *args, **kwargs):
        """Writes (appends) the input entry to a given file."""
        # FIXME: opening the file per entry is not optimal. Use writelines?
        with open(self._filepath, 'a') as f:
            f.write(f"{str(entry)}\n")


class NullWriter(BaseWriter):
    """Null writer."""
