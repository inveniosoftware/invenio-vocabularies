# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Datastreams module."""

from .datastreams import DataStream, StreamEntry
from .factories import DataStreamFactory

__all__ = (
    "DataStream",
    "DataStreamFactory",
    "StreamEntry",
)
