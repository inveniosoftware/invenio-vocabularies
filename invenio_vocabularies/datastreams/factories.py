# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Data stream factory."""

from flask import current_app

from .datastreams import DataStream
from .errors import FactoryError


class OptionsConfigMixin:
    """Options from config mixin."""

    CONFIG_VAR = None

    @classmethod
    def options(cls):
        """Reads the possible options form config."""
        return current_app.config.get(cls.CONFIG_VAR, {})


class Factory:
    """Factory."""

    FACTORY_NAME = None

    @classmethod
    def create(cls, config):
        """Creats a factory from config."""
        try:
            type_ = config["type"]
            args = config.get("args", {})
            return cls.options()[type_](**args)
        except KeyError:
            raise FactoryError(name=cls.FACTORY_NAME, key=type_)


class WriterFactory(Factory, OptionsConfigMixin):
    """Writer factory."""

    FACTORY_NAME = "Writer"
    CONFIG_VAR = "VOCABULARIES_DATASTREAM_WRITERS"


class ReaderFactory(Factory, OptionsConfigMixin):
    """Reader factory."""

    FACTORY_NAME = "Reader"
    CONFIG_VAR = "VOCABULARIES_DATASTREAM_READERS"


class TransformerFactory(Factory, OptionsConfigMixin):
    """Transformer factory."""

    FACTORY_NAME = "Transformer"
    CONFIG_VAR = "VOCABULARIES_DATASTREAM_TRANSFORMERS"


class DataStreamFactory:
    """Data streams factory."""

    @classmethod
    def create(cls, readers_config, writers_config, transformers_config=None, **kwargs):
        """Creates a data stream based on the config."""
        readers = []
        for r_conf in readers_config:
            readers.append(ReaderFactory.create(r_conf))

        writers = []
        for w_conf in writers_config:
            writers.append(WriterFactory.create(w_conf))

        transformers = []
        if transformers_config:
            for t_conf in transformers_config:
                transformers.append(TransformerFactory.create(t_conf))

        return DataStream(
            readers=readers, writers=writers, transformers=transformers, **kwargs
        )
