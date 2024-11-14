# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary permissions."""

from invenio_records_permissions import RecordPermissionPolicy
from invenio_records_permissions.generators import AnyUser, SystemProcess

from invenio_vocabularies.services.generators import IfTags


class PermissionPolicy(RecordPermissionPolicy):
    """Permission policy."""

    can_search = [SystemProcess(), AnyUser()]
    can_read = [
        SystemProcess(),
        IfTags(["unlisted"], then_=[SystemProcess()], else_=[AnyUser()]),
    ]
    can_create = [SystemProcess()]
    can_update = [SystemProcess()]
    can_delete = [SystemProcess()]
    can_manage = [SystemProcess()]
    # this permission is needed for the /api/vocabularies/ endpoint
    can_list_vocabularies = [SystemProcess(), AnyUser()]
