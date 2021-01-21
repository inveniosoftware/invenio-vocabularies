# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary permissions."""

from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import AnyUser


class PermissionPolicy(RecordPermissionPolicy):
    """Permission policy."""

    # TODO: restrict to not allow create/update/delete
    can_search = [AnyUser()]
    can_create = [AnyUser()]
    can_read = [AnyUser()]
    can_update = [AnyUser()]
    can_delete = [AnyUser()]
    can_manage = [AnyUser()]

    # Type permissions
    can_manage = [AnyUser()]
