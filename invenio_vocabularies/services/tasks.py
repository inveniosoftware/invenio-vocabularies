# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
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
    )

    for result in ds.process():
        if result.errors:
            for err in result.errors:
                current_app.logger.error(err)


def process_chunk(ids):
    """Process a chunk."""
    # FIXME: how to deal with vocabularies using different services
    # e.g. contrib + generic
    updated_vocabs = vocab_service.read_many(identity, ids)
    query = ...
    to_update = rec_service.search(query)
    for rec in to_update:
        # how to find them?
        # - we can hardcode paths
        # - access `relations` attribute (data access layer)
        for vocab in updated_vocabs:  # maybe build an inv idx
            updated_rec = update_metadata(rec)
            rec_service.update(identity, updated_rec)


@shared_task(ignore_result=True)
def update_dereferenced_vocabularies(updated_vocabulary_ids):
    """Update dereferrenced vocabularies in records."""
    # FIXME: config? sensitive value?
    IDS_THRESHOLD = 1000
    # FIXME: can use more-itertools.sliced
    chunks = int(len(updated_vocabulary_ids)/IDS_THRESHOLD)
    reminder = len(updated_vocabulary_ids) % IDS_THRESHOLD

    for c_idx in range(chunks):
        lower = c_idx*IDS_THRESHOLD
        upper = (c_idx+1)*IDS_THRESHOLD
        process_chunk(updated_vocabulary_ids[lower:upper])

    process_chunk(updated_vocabulary_ids[-reminder:])
