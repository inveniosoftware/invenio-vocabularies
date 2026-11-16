# SPDX-FileCopyrightText: 2021-2024 CERN.
# SPDX-FileCopyrightText: 2024 KTH Royal Institute of Technology.
# SPDX-License-Identifier: MIT

"""CLI Module tests."""

import tarfile
from pathlib import Path

import pytest
from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry

from invenio_vocabularies.cli import _process_vocab, vocabularies
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
from invenio_vocabularies.factories import get_vocabulary_config
from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.models import VocabularyType


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
    vocab_factory = get_vocabulary_config("names")
    config = vocab_factory.get_config(origin=names_tar_file.absolute())
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


@pytest.fixture()
def license_items(db, service, identity):
    """Create a second generic vocabulary with a couple of items."""
    VocabularyType.create(id="licenses", pid_type="lic")
    db.session.commit()
    for id_ in ["cc-by-4.0", "cc0-1.0"]:
        service.create(identity, {"id": id_, "title": {"en": id_}, "type": "licenses"})
    Vocabulary.index.refresh()


def _ids(service, identity, type_):
    """Return the ids of the non-deleted items of a vocabulary type."""
    Vocabulary.index.refresh()
    return {hit["id"] for hit in service.search(identity, type=type_).hits}


def test_delete_generic_item(app, search_clear, service, identity, lang_data_many):
    runner = app.test_cli_runner()
    result = runner.invoke(vocabularies, ["delete", "-v", "languages", "-i", "fr"])

    assert result.exit_code == 0
    assert "fr deleted from languages" in result.output
    assert _ids(service, identity, "languages") == {"tr", "gr", "ger", "es"}


def test_delete_generic_multiple_ids(
    app, search_clear, service, identity, lang_data_many
):
    runner = app.test_cli_runner()
    result = runner.invoke(
        vocabularies, ["delete", "-v", "languages", "-i", "fr", "-i", "es"]
    )

    assert result.exit_code == 0
    assert "2 items deleted" in result.output
    assert _ids(service, identity, "languages") == {"tr", "gr", "ger"}


def test_delete_generic_all_scoped_to_type(
    app, search_clear, service, identity, lang_data_many, license_items
):
    runner = app.test_cli_runner()
    result = runner.invoke(vocabularies, ["delete", "-v", "languages", "--all"])

    assert result.exit_code == 0
    assert _ids(service, identity, "languages") == set()
    assert _ids(service, identity, "licenses") == {"cc-by-4.0", "cc0-1.0"}


def test_delete_generic_not_found(app, search_clear, service, identity, lang_data_many):
    runner = app.test_cli_runner()
    result = runner.invoke(
        vocabularies, ["delete", "-v", "languages", "-i", "does-not-exist"]
    )

    assert result.exit_code == 0
    assert "PID does-not-exist not found" in result.output
    assert "1 not found" in result.output


def test_delete_unknown_vocabulary(app, db):
    runner = app.test_cli_runner()
    result = runner.invoke(vocabularies, ["delete", "-v", "unknown", "-i", "foo"])

    assert result.exit_code == 1
    assert "Unknown vocabulary unknown" in result.output
