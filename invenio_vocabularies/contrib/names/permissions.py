# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary permissions."""

from invenio_records_permissions.generators import AuthenticatedUser, SystemProcess

from invenio_vocabularies.services.generators import IfTags
from invenio_vocabularies.services.permissions import PermissionPolicy


class NamesPermissionPolicy(PermissionPolicy):
    """Names permission policy.

    Names endpoints are protected, only authenticated users can access them.
    """

    can_search = [
        SystemProcess(),
        AuthenticatedUser(),
    ]
    can_read = [
        SystemProcess(),
        IfTags(["unlisted"], then_=[SystemProcess()], else_=[AuthenticatedUser()]),
    ]
