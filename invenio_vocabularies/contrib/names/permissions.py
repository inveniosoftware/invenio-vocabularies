# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary permissions."""

from invenio_records_permissions.generators import AuthenticatedUser, SystemProcess

from invenio_vocabularies.services.generators import Tags
from invenio_vocabularies.services.permissions import PermissionPolicy


class NamesPermissionPolicy(PermissionPolicy):
    """Names permission policy."""

    can_search = [
        SystemProcess(),
        Tags(exclude=["non-searchable"], only_authenticated=True),
    ]
    can_read = [SystemProcess(), AuthenticatedUser()]
    # this permission is needed for the /api/vocabularies/ endpoint
    can_list_vocabularies = [
        SystemProcess(),
        Tags(exclude=["non-searchable"], only_authenticated=True),
    ]
