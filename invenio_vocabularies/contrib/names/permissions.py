# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary permissions."""

from invenio_records_permissions.generators import AuthenticatedUser, SystemProcess

from ...services.permissions import PermissionPolicy


class NamesPermissionPolicy(PermissionPolicy):
    """Permission policy."""

    can_search = [SystemProcess(), AuthenticatedUser()]
    can_read = [SystemProcess(), AuthenticatedUser()]
