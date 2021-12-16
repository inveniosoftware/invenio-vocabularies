# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Data stream factory."""

from flask import current_app

from .datastreams import BaseDataStream
from .errors import FactoryError


class OptionsConfigMixin:
    """Options from config mixin."""

    CONFIG_VAR = None

    @classmethod
    def options(cls):
        """Reads the possible options form config."""
        return current_app.config.get(cls.CONFIG_VAR, {})


class BaseFactory:
    """Base factory."""

    FACTORY_NAME = None

    @classmethod
    def create(cls, config):
        """Creates a transformer from config."""
        try:
            type_ = config["type"]
            args = config.get("args", {})

            return cls.options()[type_](**args)
        except KeyError:
            raise FactoryError(name=cls.FACTORY_NAME, key=type_)


class WriterFactory(BaseFactory, OptionsConfigMixin):
    """Writer factory."""

    FACTORY_NAME = "Writer"
    CONFIG_VAR = "VOCABULARIES_DATASTREAM_WRITERS"


class ReaderFactory(BaseFactory, OptionsConfigMixin):
    """Reader factory."""

    FACTORY_NAME = "Reader"
    CONFIG_VAR = "VOCABULARIES_DATASTREAM_READERS"


class TransformerFactory(BaseFactory, OptionsConfigMixin):
    """Transformer factory."""

    FACTORY_NAME = "Transformer"
    CONFIG_VAR = "VOCABULARIES_DATASTREAM_TRANSFORMERS"


class DataStreamFactory:
    """Data streams factory."""

    @classmethod
    def create(
        cls, reader_config, writers_config, transformers_config=None, **kwargs
    ):
        """Creates a data stream based on the config."""
        reader = ReaderFactory.create(reader_config)
        writers = []
        for w_conf in writers_config:
            writers.append(WriterFactory.create(w_conf))

        transformers = []
        if transformers_config:
            for t_conf in transformers_config:
                transformers.append(TransformerFactory.create(t_conf))

        return BaseDataStream(
            reader=reader, writers=writers, transformers=transformers
        )
