# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Commands to create and manage vocabulary."""

import json

import click
from flask.cli import with_appcontext
from invenio_db import db

from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.models import VocabularyMetadata, \
    VocabularyType
from invenio_vocabularies.services.records.service import Service


@click.group()
def load():
    """Load vocabulary."""
    pass


@load.command(name="json")
@click.argument("filenames", nargs=-1)
@with_appcontext
def json_files(filenames):
    """Index JSON-based vocabularies in Elasticsearch."""
    source = "json"

    indexer = Service().indexer
    for filename in filenames:
        click.echo("indexing vocabularies in {}...".format(filename))
        items = load_vocabulary(source, filename)
        with click.progressbar(items) as bar:
            for item in bar:
                indexer.index(item)
        click.echo("indexed vocabulary")


def load_vocabulary(source, filename):
    """Load vocabulary items from a vocabulary source."""
    assert source == "json"
    records = []
    with open(filename) as json_file:
        json_array = json.load(json_file)
        assert len(json_array) > 0
        vocabulary_type_name = json_array[0]["type"]
        vocabulary_type = VocabularyType(name=vocabulary_type_name)
        db.session.add(vocabulary_type)
        for item_data in json_array:
            assert item_data["type"] == vocabulary_type_name
            vocabulary_item = Vocabulary.create(
                item_data, vocabulary_type=vocabulary_type.id)
            records.append(vocabulary_item)
    db.session.commit()
    return records
