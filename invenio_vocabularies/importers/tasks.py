# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks for importers."""

from celery import shared_task
from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry


@shared_task
def create_vocabulary_record(service_str, data):
    """Create a vocabulary record."""
    service = current_service_registry.get(service_str)
    service.create(system_identity, data)
