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


def _process_vocab(config, num_samples=None):
    """Import a vocabulary."""
    ds = DataStreamFactory.create(
        reader_config=config["reader"],
        transformers_config=config.get("transformers"),
        writers_config=config["writers"],
    )

    success, errored = 0, 0
    left = num_samples or -1
    for result in ds.process():
        left = left - 1
        if result.errors:
            for err in result.errors:
                click.secho(err, fg="red")
            errored += 1
        else:
            success += 1
        if left == 0:
            click.secho(f"Number of samples reached {num_samples}", fg="green")
            break
    return success, errored


def _output_process(vocabulary, op, success, errored):
    """Outputs the result of an operation."""
    total = success + errored

    color = "green"
    if errored:
        color = "yellow" if success else "red"

    click.secho(
        f"Vocabulary {vocabulary} {op}. Total items {total}. \n"
        f"{success} items succeeded, {errored} contained errors.",
        fg=color
    )


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

    config = get_config_for_ds(vocabulary, filepath, origin)
    success, errored = _process_vocab(config, num_samples)

    _output_process(vocabulary, "loaded", success, errored)


@vocabularies.command()
@click.option("-v", "--vocabulary", type=click.STRING, required=True)
@click.option("-f", "--filepath", type=click.STRING)
@click.option("-o", "--origin", type=click.STRING)
@click.option("-t", "--target", type=click.STRING)
@click.option("-n", "--num-samples", type=click.INT)
@with_appcontext
def convert(
    vocabulary, filepath=None, origin=None, target=None, num_samples=None
):
    """Convert a vocabulary to a new format."""
    if not filepath and (not origin or not target):
        click.secho(
            "One of --filepath or --origin and --target must be present",
            fg="red"
        )
        exit(1)

    config = get_config_for_ds(vocabulary, filepath, origin)
    if not filepath:
        config["writers"] = [
            {"type": "yaml", "args": {"filepath": target}}
        ]

    success, errored = _process_vocab(config, num_samples)
    _output_process(vocabulary, "converted", success, errored)
