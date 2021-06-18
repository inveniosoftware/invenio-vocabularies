# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary affiliations PID provider."""

from invenio_pidstore.models import PIDStatus
from invenio_pidstore.providers.base import BaseProvider


class AffiliationProvider(BaseProvider):
    """Affiliations PID provider."""

    pid_type = 'affid'
    """Type of persistent identifier."""

    @classmethod
    def create(cls, object_type=None, object_uuid=None, record=None, **kwargs):
        """Create a new affiliation identifier.

        Relies on the record having already a pid_value.

        For more information about parameters,
        see :meth:`invenio_pidstore.providers.base.BaseProvider.create`.

        :param object_type: The object type. (Default: None.)
        :param object_uuid: The object identifier. (Default: None).
        :param record: An affiliation vocabulary record.
        :param kwargs: Addtional options
        :returns: A :class:`AffiliationProvider` instance.
        """
        assert record is not None, "Missing or invalid 'record'."
        assert 'id' in record and \
            isinstance(record['id'], str), "Missing 'id' key in record."

        # Retrieve pid value form record.
        pid_value = record['id']

        # You must assign immediately.
        assert object_uuid
        assert object_type

        return super().create(
            pid_type=cls.pid_type,
            pid_value=pid_value,
            object_type=object_type,
            object_uuid=object_uuid,
            status=PIDStatus.REGISTERED
        )
