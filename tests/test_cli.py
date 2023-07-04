# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""CLI Module tests."""

import tarfile
from pathlib import Path

import pytest
from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry

from invenio_vocabularies.cli import _process_vocab, get_config_for_ds, vocabularies
from invenio_vocabularies.config import (
    VOCABULARIES_DATASTREAM_TRANSFORMERS,
    VOCABULARIES_DATASTREAM_WRITERS,
)
from invenio_vocabularies.contrib.names.api import Name
from invenio_vocabularies.contrib.names.datastreams import (
    VOCABULARIES_DATASTREAM_TRANSFORMERS as NAMES_TRANSFORMERS,
)
from invenio_vocabularies.contrib.names.datastreams import (
    VOCABULARIES_DATASTREAM_WRITERS as NAMES_WRITERS,
)


@pytest.fixture(scope="module")
def app_config(app_config):
    """Mimic an instance's configuration."""
    app_config["VOCABULARIES_DATASTREAM_TRANSFORMERS"] = {
        **VOCABULARIES_DATASTREAM_TRANSFORMERS,
        **NAMES_TRANSFORMERS,
    }
    app_config["VOCABULARIES_DATASTREAM_WRITERS"] = {
        **VOCABULARIES_DATASTREAM_WRITERS,
        **NAMES_WRITERS,
    }

    return app_config


@pytest.fixture(scope="module")
def name_xml():
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<record:record path="/0000-0001-8135-3489">\n'
        "    <common:orcid-identifier>\n"
        "        <common:uri>https://orcid.org/0000-0001-8135-3489</common:uri>\n"  # noqa
        "        <common:path>0000-0001-8135-3489</common:path>\n"
        "        <common:host>orcid.org</common:host>\n"
        "    </common:orcid-identifier>\n"
        '    <person:person path="/0000-0001-8135-3489/person">\n'
        '        <person:name visibility="public" path="0000-0001-8135-3489">\n'  # noqa
        "            <personal-details:given-names>Lars Holm</personal-details:given-names>"  # noqa
        "            <personal-details:family-name>Nielsen</personal-details:family-name>\n"  # noqa
        "        </person:name>\n"
        '        <external-identifier:external-identifiers path="/0000-0001-8135-3489/external-identifiers"/>\n'  # noqa
        "    </person:person>\n"
        '    <activities:activities-summary path="/0000-0001-8135-3489/activities">\n'  # noqa
        '       <activities:employments path="/0000-0001-8135-3489/employments">\n'  # noqa
        "           <employments:affiliation-group>\n"
        "               <employments:employment-summary>\n"
        "                   <employment-summary:organization>\n"
        "                       <organization:name>CERN</organization:name>\n"
        "                   </employment-summary:organization>\n"
        "               </employments:employment-summary>\n"
        "           </employments:affiliation-group>\n"
        "       </activities:employments>\n"
        "    </activities:activities-summary>\n"
        "</record:record>\n"
    )


@pytest.fixture(scope="function")
def names_tar_file(name_xml):
    """Creates a Tar file with three files (two yaml) inside.

    Each iteration should return the content of one yaml file,
    it should ignore the .other file.
    """
    filename = Path("cli_test.tar.gz")
    with tarfile.open(filename, "w:gz") as tar:
        inner_filename = Path("lnielsen_name.xml")
        with open(inner_filename, "w") as file:
            file.write(name_xml)
        tar.add(inner_filename)
        inner_filename.unlink()

    yield filename

    filename.unlink()  # delete created file


def test_process(app, names_tar_file):
    service = current_service_registry.get("names")
    config = get_config_for_ds(vocabulary="names", origin=names_tar_file.absolute())
    _process_vocab(config)
    Name.index.refresh()

    orcid = "0000-0001-8135-3489"
    results = service.search(system_identity, q=f"identifiers.identifier:{orcid}")

    assert results.total == 1
    assert list(results.hits)[0]["identifiers"][0]["identifier"] == orcid


def test_update_cmd(app, names_tar_file):
    # cli update
    runner = app.test_cli_runner()
    result = runner.invoke(
        vocabularies,
        ["update", "-v", "names", "--origin", names_tar_file.absolute()],
    )
    assert result.exit_code == 0
