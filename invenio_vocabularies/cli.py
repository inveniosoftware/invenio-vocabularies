# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Commands to create and manage vocabulary."""

import csv
from os.path import dirname, join

import click
from flask.cli import with_appcontext
from flask_principal import Identity
from invenio_access import any_user
from invenio_db import db

from invenio_vocabularies.contrib.subjects.subjects import subject_record_type
from invenio_vocabularies.records.models import VocabularyType
from invenio_vocabularies.services.service import VocabulariesService

data_directory = join(dirname(__file__), "data")


def get_available_vocabularies():
    """Specify the available vocabularies."""
    return {
        "licenses": {
            "path": join(data_directory, "licenses.csv"),
        },
        "subjects": {
            "path": join(data_directory, "subjects.csv"),
            "specific": _create_subjects_vocabulary,
        },
    }


def _load_csv_data(path):
    with open(path) as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        dicts = [row for row in reader]
        return dicts


def _create_subjects_vocabulary(vocabulary_type_name, source_path):
    identity = Identity(1)
    identity.provides.add(any_user)
    service = subject_record_type.service_cls()

    rows = _load_csv_data(source_path)

    records = []
    for row in rows:
        metadata = {
            "title": row["title"],
            "term": row["id"],
            "identifier": row["id"],
            "scheme": row["scheme"],
        }

        record = service.create(
            identity=identity,
            data={
                "metadata": metadata,
            },
        )

        records.append(record)

    return records


def _create_vocabulary(vocabulary_type_name, source_path):
    identity = Identity(1)
    identity.provides.add(any_user)
    service = VocabulariesService()

    # Load data
    rows = _load_csv_data(source_path)

    # Create vocabulary type
    vocabulary_type = VocabularyType(name=vocabulary_type_name)
    db.session.add(vocabulary_type)
    db.session.commit()

    i18n = ["title", "description"]  # Attributes with i18n support
    other = ["icon"]  # Other top-level attributes

    default_language = "en"  # Static (dependent on the files)

    metadata = {"title": {}, "description": {}, "props": {}}

    records = []
    for row in rows:
        for attribute in row:
            value = row[attribute]
            if attribute in i18n:
                metadata[attribute][default_language] = value
            elif any(map(lambda s: value.startswith(s + "_"), i18n)):
                [prefix_attr, language] = attribute.split("_", 1)
                metadata[prefix_attr][language] = value
            elif attribute in other:
                metadata[attribute] = value
            else:
                metadata["props"][attribute] = value

        # Create record
        record = service.create(
            identity=identity,
            data={
                "metadata": metadata,
                "vocabulary_type_id": vocabulary_type.id,
            },
        )

        records.append(record)

    return records


@click.group()
def vocabularies():
    """Vocabularies command."""
    pass


@vocabularies.command(name="import")
@click.argument(
    "vocabulary_types",
    nargs=-1,
    type=click.Choice([v for v in get_available_vocabularies()]),
)
@with_appcontext
def load(vocabulary_types):
    """Index CSV-based vocabularies in Elasticsearch."""
    click.echo("creating vocabularies...", color="blue")

    for vocabulary_type in vocabulary_types:
        vocabulary = get_available_vocabularies()[vocabulary_type]
        if VocabularyType.query.filter_by(name=vocabulary_type).count() > 0:
            click.echo(
                "vocabulary type {} already exists, skipping".format(
                    vocabulary_type
                ),
                color="red",
            )
            continue

        click.echo(
            "creating vocabulary type {}...".format(vocabulary_type),
            color="blue",
        )

        fun_create_vocabulary = vocabulary.get("specific", _create_vocabulary)
        items = fun_create_vocabulary(vocabulary_type, vocabulary["path"])

        click.echo(
            "created {} vocabulary items successfully".format(len(items)),
            color="green",
        )
    click.echo("vocabularies created", color="green")
