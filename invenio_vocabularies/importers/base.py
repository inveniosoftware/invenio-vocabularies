# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base importer."""

import yaml


class BaseImporter:
    """Fixture loading mixin."""

    def __init__(self, search_paths, filename):
        """Initialize the fixture."""
        self._search_paths = search_paths
        self._filename = filename

    def load(self):
        """Load the fixture.

        The first file matching the filename found in self._search_paths is
        chosen.
        """
        for path in self._search_paths:
            filepath = path / self._filename

            # Providing a yaml file is optional
            if not filepath.exists():
                continue

            with open(filepath) as fp:
                data = yaml.safe_load(fp) or []
                for item in data:
                    self.create(item)

            break

    def read(self):
        """Read the entries.

        The first file matching the filename found in self._search_paths is
        chosen.
        """
        for path in self._search_paths:
            filepath = path / self._filename

            # Providing a yaml file is optional
            if not filepath.exists():
                continue

            with open(filepath) as fp:
                return list(yaml.safe_load(fp)) or []
            break
