# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Subjects services."""


from .subjects import record_type

SubjectsServiceConfig = record_type.service_config_cls

SubjectsService = record_type.service_cls
