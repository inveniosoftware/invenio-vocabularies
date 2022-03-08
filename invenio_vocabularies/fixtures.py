# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Fixtures module."""

import yaml
from invenio_access.permissions import system_identity

from .datastreams.factories import DataStreamFactory
from .proxies import current_service


class VocabularyFixture:
    """Vocabulary fixture."""

    def __init__(self, filepath, delay=True):
        """Constructor."""
        self._filepath = filepath

    def _load_vocabulary(self, config, delay=True, **kwargs):
        """Given an entry from the vocabularies.yaml file, load its content."""
        datastream = DataStreamFactory.create(
            readers_config=config["readers"],
            transformers_config=config.get("transformers"),
            writers_config=config["writers"],
        )

        errors = []
        for result in datastream.process():
            if result.errors:
                errors.append(result)

        return errors

    def _create_vocabulary(self, id_, pid_type, *args, **kwargs):
        """Creates a vocabulary."""
        return current_service.create_type(system_identity, id_, pid_type)

    def load(self, *args, **kwargs):
        """Return content of vocabularies file."""
        with open(self._filepath) as f:
            data = yaml.safe_load(f) or {}
            for id_, config in data.items():
                self._create_vocabulary(id_, config["pid-type"])
                yield self._load_vocabulary(config)
