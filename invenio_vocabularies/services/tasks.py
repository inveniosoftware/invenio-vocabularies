# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks."""

from celery import shared_task
from flask import current_app

from ..datastreams.factories import DataStreamFactory


@shared_task(ignore_result=True)
def process_datastream(config):
    """Process a datastream from config."""
    ds = DataStreamFactory.create(
        readers_config=config["readers"],
        transformers_config=config.get("transformers"),
        writers_config=config["writers"],
        batch_size=config.get("batch_size", 1000),
        write_many=config.get("write_many", False),
    )

    for result in ds.process():
        if result.errors:
            for err in result.errors:
                current_app.logger.error(err)
