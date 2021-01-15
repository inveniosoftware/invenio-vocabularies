# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary subjects."""

from invenio_records_resources.factories.factory import RecordTypeFactory

from invenio_vocabularies.contrib.subjects.permissions import PermissionPolicy
from invenio_vocabularies.contrib.subjects.schema import SubjectSchema

subject_record_type = RecordTypeFactory(
    "Subject", SubjectSchema,
    permission_policy_cls=PermissionPolicy,
    endpoint_route='/subjects'
)
