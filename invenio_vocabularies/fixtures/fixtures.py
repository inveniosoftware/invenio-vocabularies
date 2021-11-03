# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Fixtures module."""

import yaml
from flask import current_app

from .factories import DataStreamFactory, WriterFactory


class BaseFixture:
    """Base vocabulary fixture."""

    def __init__(self, filepath, delay=True):
        """Constructor."""
        self._filepath = filepath

    # potential `ignore` and `force` arguments to support updating entries
    # TODO: bulk writting
    def _load_vocabulary(self, config, delay=True, **kwargs):
        """Given an entry from the vocabularies.yaml file, load its content."""
        # TODO: write with delay (tasks encapsulation needed)
        datastream = DataStreamFactory.create(
            reader_config=config["reader"],
            transformers_config=config.get("transformers"),
            writers_config=config["writers"],
        )

        errors = []
        for result in datastream.process():
            if result.errors:
                errors.append(result)

        return errors

    # TODO: support vocabularies with schemes (subvocabs)
    def _create_vocabulary(self, id_, pid_type, *args, **kwargs):
        """Creates a vocabulary."""
        pass

    # TODO: support bulk import (e.g. db commit per item + bulk indexing)
    def load(self, *args, **kwargs):
        """Return content of vocabularies file."""
        with open(self._filepath) as f:
            data = yaml.safe_load(f) or {}
            for id_, config in data.items():
                self._create_vocabulary(id_, config["pid-type"])
                yield self._load_vocabulary(config)
