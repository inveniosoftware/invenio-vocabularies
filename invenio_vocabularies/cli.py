# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Commands to create and manage vocabularies."""

import click
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDDeletedError, PIDDoesNotExistError

from .datastreams import DataStreamFactory
from .factories import get_vocabulary_config


@click.group()
def vocabularies():
    """Vocabularies command."""


def _process_vocab(config, num_samples=None):
    """Import a vocabulary."""
    ds = DataStreamFactory.create(
        readers_config=config["readers"],
        transformers_config=config.get("transformers"),
        writers_config=config["writers"],
        batch_size=config.get("batch_size", 1000),
        write_many=config.get("write_many", False),
    )

    success, errored, filtered = 0, 0, 0
    left = num_samples or -1
    for result in ds.process():
        left = left - 1
        if result.filtered:
            filtered += 1
        if result.errors:
            for err in result.errors:
                click.secho(err, fg="red")
            errored += 1
        else:
            success += 1
        if left == 0:
            click.secho(f"Number of samples reached {num_samples}", fg="green")
            break
    return success, errored, filtered


def _output_process(vocabulary, op, success, errored, filtered):
    """Outputs the result of an operation."""
    total = success + errored

    color = "green"
    if errored:
        color = "yellow" if success else "red"

    click.secho(
        f"Vocabulary {vocabulary} {op}. Total items {total}. \n"
        f"{success} items succeeded\n"
        f"{errored} contained errors\n"
        f"{filtered} were filtered.",
        fg=color,
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
        click.secho("One of --filepath or --origin must be present.", fg="red")
        exit(1)

    vc = get_vocabulary_config(vocabulary)
    config = vc.get_config(filepath, origin)

    success, errored, filtered = _process_vocab(config, num_samples)

    _output_process(vocabulary, "imported", success, errored, filtered)


@vocabularies.command()
@click.option("-v", "--vocabulary", type=click.STRING, required=True)
@click.option("-f", "--filepath", type=click.STRING)
@click.option("-o", "--origin", type=click.STRING)
@with_appcontext
def update(vocabulary, filepath=None, origin=None):
    """Import a vocabulary."""
    if not filepath and not origin:
        click.secho("One of --filepath or --origin must be present.", fg="red")
        exit(1)
    vc = get_vocabulary_config(vocabulary)
    config = vc.get_config(filepath, origin)

    for w_conf in config["writers"]:
        if w_conf["type"] == "async":
            w_conf_update = w_conf["args"]["writer"]
        else:
            w_conf_update = w_conf

        if "args" in w_conf_update:
            w_conf_update["args"]["update"] = True
        else:
            w_conf_update["args"] = {"update": True}

    success, errored, filtered = _process_vocab(config)

    _output_process(vocabulary, "updated", success, errored, filtered)


@vocabularies.command()
@click.option("-v", "--vocabulary", type=click.STRING, required=True)
@click.option("-f", "--filepath", type=click.STRING)
@click.option("-o", "--origin", type=click.STRING)
@click.option("-t", "--target", type=click.STRING)
@click.option("-n", "--num-samples", type=click.INT)
@with_appcontext
def convert(vocabulary, filepath=None, origin=None, target=None, num_samples=None):
    """Convert a vocabulary to a new format."""
    if not filepath and (not origin or not target):
        click.secho(
            "One of --filepath or --origin and --target must be present.", fg="red"
        )
        exit(1)

    vc = get_vocabulary_config(vocabulary)
    config = vc.get_config(filepath, origin)
    if not filepath:
        config["writers"] = [{"type": "yaml", "args": {"filepath": target}}]

    success, errored, filtered = _process_vocab(config, num_samples)
    _output_process(vocabulary, "converted", success, errored, filtered)


@vocabularies.command()
@click.option("-v", "--vocabulary", type=click.STRING, required=True)
@click.option(
    "-i",
    "--identifier",
    type=click.STRING,
    help="Identifier of the vocabulary item to delete.",
)
@click.option("--all", is_flag=True, default=False)
@with_appcontext
def delete(vocabulary, identifier, all):
    """Delete all items or a specific one of the vocabulary."""
    if not identifier and not all:
        click.secho("An identifier or the --all flag must be present.", fg="red")
        exit(1)

    vc = get_vocabulary_config(vocabulary)
    service = vc.get_service()
    if identifier:
        try:
            if service.delete(system_identity, identifier):
                click.secho(f"{identifier} deleted from {vocabulary}.", fg="green")
        except (PIDDeletedError, PIDDoesNotExistError):
            click.secho(f"PID {identifier} not found.")
    elif all:
        items = service.scan(system_identity)
        for item in items.hits:
            try:
                if service.delete(system_identity, item["id"]):
                    click.secho(f"{item['id']} deleted from {vocabulary}.", fg="green")
            except (PIDDeletedError, PIDDoesNotExistError):
                click.secho(f"PID {item['id']} not found.")
