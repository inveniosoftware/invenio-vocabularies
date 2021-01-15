# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Persistent identifier provider for vocabularies."""


from invenio_pidstore.models import PIDStatus
from invenio_pidstore.providers.base import BaseProvider


class VocabularyIdProvider(BaseProvider):
    """Vocabulary identifier provider.

    This PID provider requires a Vocabulary record to be passed, and relies
    on the vocabulary record having an 'id' key and a type defined.
    """

    @classmethod
    def create(cls, object_type=None, object_uuid=None, record=None, **kwargs):
        """Create a new vocabulary identifier.

        Relies on the a vocabulary record being

        Note: if the object_type and object_uuid values are passed, then the
        PID status will be automatically setted to
        :attr:`invenio_pidstore.models.PIDStatus.REGISTERED`.

        For more information about parameters,
        see :meth:`invenio_pidstore.providers.base.BaseProvider.create`.

        :param object_type: The object type. (Default: None.)
        :param object_uuid: The object identifier. (Default: None).
        :param record: A vocabulary record.
        :param kwargs: Addtional options
        :returns: A :class:`VocabularyIdProvider` instance.
        """
        assert record is not None, "Missing or invalid 'record'."
        assert 'id' in record and \
            isinstance(record['id'], str), "Missing 'id' key in record."

        # Retrieve pid type from type.
        pid_type = record.type.pid_type
        # Retrieve pid type from type.
        pid_value = record['id']

        # You must assign immediately.
        assert object_uuid
        assert object_type

        return super().create(
            pid_type=pid_type,
            pid_value=pid_value,
            object_type=object_type,
            object_uuid=object_uuid,
            status=PIDStatus.REGISTERED
        )
