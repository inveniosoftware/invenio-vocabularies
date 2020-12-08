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
from flask_principal import Identity
from invenio_access import any_user
from invenio_db import db

from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.models import VocabularyMetadata, \
    VocabularyType
from invenio_vocabularies.services.records.service import VocabulariesService


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

    for filename in filenames:
        click.echo("creating vocabularies in {}...".format(filename))
        items = load_vocabulary(source, filename)
        click.echo(
            "created {} vocabulary items successfully".format(len(items))
        )


def load_vocabulary(source, filename):
    """Load vocabulary items from a vocabulary source."""
    assert source == "json"
    records = []

    identity = Identity(1)
    identity.provides.add(any_user)
    service = VocabulariesService()

    with open(filename) as json_file:
        json_array = json.load(json_file)
        assert len(json_array) > 0
        vocabulary_type_name = json_array[0]["type"]
        vocabulary_type = VocabularyType(name=vocabulary_type_name)
        db.session.add(vocabulary_type)
        db.session.commit()

        with click.progressbar(json_array) as bar:
            for item_data in bar:
                # ensure each item is of the same type
                assert item_data["type"] == vocabulary_type_name

                copied_data = {}
                for key in item_data:
                    value = item_data[key]
                    if key != "type" and key != "id" and value is not None:
                        copied_data[key] = value

                vocabulary_item_record = service.create(
                    identity=identity,
                    data={
                        "metadata": copied_data,
                        "vocabulary_type_id": vocabulary_type.id,
                    },
                )
                records.append(vocabulary_item_record)
    return records
