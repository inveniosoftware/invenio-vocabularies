# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Readers module."""

import re
import tarfile

import yaml


class BaseReader:
    """Base reader."""

    def __init__(self, origin, *args, **kwargs):
        """Constructor."""
        self._origin = origin

    def read(self, *args, **kwargs):
        """Reads the content from the origin."""
        pass


class YamlReader(BaseReader):
    """Yaml reader."""

    def read(self):
        """Reads a yaml file and returns a dictionary per element."""
        with open(self._origin) as f:
            data = yaml.safe_load(f) or []
            for entry in data:
                yield entry


class TarReader(BaseReader):
    """Tar reader."""

    def __init__(self, *args, mode="r|gz", regex=None, **kwargs):
        """Constructor."""
        self._regex = re.compile(regex) if regex else None
        self._mode = mode
        super().__init__(*args, **kwargs)

    def read(self):
        """Opens a tar and iterates through the files in the archive."""
        with tarfile.open(self._origin, self._mode) as archive:
            for member in archive:
                match = not self._regex or self._regex.search(member.name)
                if member.isfile() and match:
                    content = archive.extractfile(member).read()
                    yield content
