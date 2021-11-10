# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Commands to create and manage vocabularies."""

from copy import deepcopy

import click
import yaml
from flask.cli import with_appcontext

from .contrib.names.datastreams import DATASTREAM_CONFIG as names_ds_config
from .datastreams import DataStreamFactory


def get_config_for_ds(vocabulary, filepath=None, origin=None):
    """Calculates the configuration for a Data Stream."""
    if vocabulary == "names":  # FIXME: turn into a proper factory
        config = deepcopy(names_ds_config)
        if filepath:
            config = yaml.load(filepath).get(vocabulary)
        if origin:
            config["reader"]["args"]["origin"] = origin

        return config


@click.group()
def vocabularies():
    """Vocabularies command."""
    pass


def _import_vocab(vocabulary, filepath=None, origin=None, num_samples=None):
    """Import a vocabulary."""
    config = get_config_for_ds(vocabulary, filepath, origin)
    ds = DataStreamFactory.create(
        reader_config=config["reader"],
        transformers_config=config.get("transformers"),
        writers_config=config["writers"],
    )

    success, errored = 0, 0
    left = num_samples or -1
    for result in ds.process():
        left = left - 1
        if left == 0:
            click.secho(f"Number of samples reached {num_samples}", fg="green")
            break
        if result.errors:
            for err in result.errors:
                click.secho(err, fg="red")
            errored += 1
        else:
            success += 1

    return success, errored


@vocabularies.command(name="import")
@click.option("-v", "--vocabulary", type=click.STRING, required=True)
@click.option("-f", "--filepath", type=click.STRING)
@click.option("-o", "--origin", type=click.STRING)
@click.option("-n", "--num-samples", type=click.INT)
@with_appcontext
def import_vocab(vocabulary, filepath=None, origin=None, num_samples=None):
    """Import a vocabulary."""
    if not filepath and not origin:
        click.secho("One of --filepath or --origin must be present", fg="red")
        exit(1)

    success, errored = _import_vocab(vocabulary, filepath, origin, num_samples)
    total = success + errored

    color = "green"
    if errored:
        color = "yellow" if success else "red"

    click.secho(
        f"Vocabulary {vocabulary} loaded. Total items {total}. \n"
        f"{success} items succeeded, {errored} contained errors.",
        fg=color
    )
