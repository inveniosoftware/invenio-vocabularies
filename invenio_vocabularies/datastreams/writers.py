# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Writers module."""

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
        self._identity = identity

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
