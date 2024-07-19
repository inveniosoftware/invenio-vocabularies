# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks."""

from celery import shared_task
from flask import current_app
from invenio_logging.structlog import LoggerFactory

from ..datastreams.factories import DataStreamFactory
from ..factories import get_vocabulary_config


@shared_task(ignore_result=True)
def process_datastream(stream):
    """Process a datastream from config."""
    try:
        stream_logger = LoggerFactory.get_logger("datastreams-" + stream)
        stream_logger.info("Starting processing")
        vc_config = get_vocabulary_config(stream)
        config = vc_config.get_config()

        if not config:
            stream_logger.error("Invalid stream configuration")
            raise ValueError("Invalid stream configuration")

        ds = DataStreamFactory.create(
            readers_config=config["readers"],
            transformers_config=config.get("transformers"),
            writers_config=config["writers"],
        )
        stream_logger.info("Datastream created")
        stream_logger.info("Processing Datastream")
        success, errored, filtered = 0, 0, 0
        for result in ds.process(
            batch_size=config.get("batch_size", 100),
            write_many=config.get("write_many", False),
            logger=stream_logger,
        ):
            if result.filtered:
                filtered += 1
                stream_logger.info(
                    "Filtered", entry=result.entry, operation=result.op_type
                )
            if result.errors:
                errored += 1
                stream_logger.error(
                    "Error",
                    entry=result.entry,
                    operation=result.op_type,
                    errors=result.errors,
                )
            else:
                success += 1
                stream_logger.info(
                    "Success", entry=result.entry, operation=result.op_type
                )
        stream_logger.info(
            "Finished processing", success=success, errored=errored, filtered=filtered
        )
    except Exception as e:
        stream_logger.exception("Error processing stream", error=e)


@shared_task()
def import_funders():
    """Import the funders vocabulary.

    Only new records are imported.
    Existing records are not updated.
    """
    vc = get_vocabulary_config("funders")
    config = vc.get_config()

    # When importing funders via a Celery task, make sure that we are automatically downloading the ROR file,
    # instead of relying on a local file on the file system.
    if config["readers"][0]["type"] == "ror-http":
        readers_config_with_ror_http = config["readers"]
    else:
        readers_config_with_ror_http = [{"type": "ror-http"}] + config["readers"]

    ds = DataStreamFactory.create(
        readers_config=readers_config_with_ror_http,
        transformers_config=config.get("transformers"),
        writers_config=config["writers"],
    )

    for result in ds.process():
        if result.errors:
            for err in result.errors:
                current_app.logger.exception(err)
