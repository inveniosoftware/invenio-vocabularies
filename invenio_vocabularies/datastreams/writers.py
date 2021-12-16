# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Writers module."""

from pathlib import Path

import yaml
from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry
from marshmallow import ValidationError

from .datastreams import StreamResult
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

    def __init__(self, service_or_name, identity, *args, **kwargs):
        """Constructor.

        :param service_or_name: a service instance or a key of the
                                service registry.
        :param identity: access identity.
        """
        if isinstance(service_or_name, str):
            service_or_name = current_service_registry.get(service_or_name)

        self._service = service_or_name
        self._identity = system_identity

        super().__init__(*args, **kwargs)

    def write(self, entry, *args, **kwargs):
        """Writes the input entry using a given service."""
        try:
            result = self._service.create(self._identity, entry)
        except ValidationError as err:
            result = StreamResult(
                entry=entry,
                errors=[{"ValidationError": err.messages}]
            )
        if result.errors:
            raise WriterError(result.errors)

        return result


class YamlWriter(BaseWriter):
    """Writes the entries to a YAML file."""

    def __init__(self, filepath, *args, **kwargs):
        """Constructor.

        :param filepath: path of the output file.
        """
        self._filepath = Path(filepath)

        super().__init__(*args, **kwargs)

    def write(self, entry, *args, **kwargs):
        """Writes the input entry using a given service."""
        with open(self._filepath, 'a') as file:
            # made into array for safer append
            # will always read array (good for reader)
            yaml.safe_dump([entry], file)
            result = StreamResult(entry=entry)

        return result
