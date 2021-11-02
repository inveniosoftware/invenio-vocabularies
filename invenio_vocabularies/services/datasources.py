# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Datasources module."""


class BaseDataSource:

    def __init__(self, *args, **kwargs):
        pass

    def iter_entries(self, *args, **kwargs):
        pass

    def transform_entry(self, *args, **kwargs):
        pass

    def count(self, *args, **kwargs):
        pass
