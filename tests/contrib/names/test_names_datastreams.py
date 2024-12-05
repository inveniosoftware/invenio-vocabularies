# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names data streams tests."""

import os
import tempfile
from copy import deepcopy
from unittest.mock import patch

import pytest
from invenio_access.permissions import system_identity
from invenio_records_resources.proxies import current_service_registry

from invenio_vocabularies.contrib.names.api import Name
from invenio_vocabularies.contrib.names.datastreams import (
    NamesServiceWriter,
    OrcidHTTPReader,
    OrcidTransformer,
)
from invenio_vocabularies.datastreams import StreamEntry
from invenio_vocabularies.datastreams.errors import TransformerError, WriterError
from invenio_vocabularies.datastreams.transformers import XMLTransformer


@pytest.fixture(scope="function")
def name_full_data():
    """Full name data."""
    return {
        "id": "0000-0001-8135-3489",
        "given_name": "Lars Holm",
        "family_name": "Nielsen",
        "name": "Nielsen, Lars Holm",
        "identifiers": [
            {
                "scheme": "orcid",
                "identifier": "0000-0001-8135-3489",  # normalized after create
            }
        ],
        "affiliations": [{"name": "CERN"}],
    }


# NOTE: This is a simplified version of the original XML data from ORCiD. Sections like
#       works, funding, educations, etc. and attributes have been removed.
XML_ENTRY_DATA = b"""
<record:record>
    <common:orcid-identifier>
        <common:uri>https://orcid.org/0000-0001-8135-3489</common:uri>
        <common:path>0000-0001-8135-3489</common:path>
        <common:host>orcid.org</common:host>
    </common:orcid-identifier>
    <person:person>
        <person:name>
            <personal-details:given-names>Lars Holm</personal-details:given-names>
            <personal-details:family-name>Nielsen</personal-details:family-name>
        </person:name>
    </person:person>
    <activities:activities-summary>
        <activities:employments>
            <activities:affiliation-group>
                <employment:employment-summary>
                    <common:start-date>
                        <common:year>2012</common:year>
                        <common:month>03</common:month>
                        <common:day>16</common:day>
                    </common:start-date>
                    <common:organization>
                        <common:name>CERN</common:name>
                        <common:disambiguated-organization>
                            <common:disambiguated-organization-identifier>https://ror.org/01ggx4157
</common:disambiguated-organization-identifier>
                            <common:disambiguation-source>ROR</common:disambiguation-source>
                        </common:disambiguated-organization>
                    </common:organization>
                </employment:employment-summary>
            </activities:affiliation-group>
            <activities:affiliation-group>
                <employment:employment-summary>
                    <common:start-date>
                        <common:year>2024</common:year>
                        <common:month>01</common:month>
                    </common:start-date>
                    <common:organization>
                        <common:name>ACME Inc.</common:name>
                        <common:disambiguated-organization>
                            <common:disambiguated-organization-identifier>grid.123456.z</common:disambiguated-organization-identifier>
                            <common:disambiguation-source>GRID</common:disambiguation-source>
                        </common:disambiguated-organization>
                    </common:organization>
                </employment:employment-summary>
            </activities:affiliation-group>
            <activities:affiliation-group>
                <employment:employment-summary >
                    <common:start-date>
                        <common:year>2007</common:year>
                        <common:month>08</common:month>
                    </common:start-date>
                    <common:end-date>
                        <common:year>2012</common:year>
                        <common:month>03</common:month>
                    </common:end-date>
                    <common:organization>
                        <common:name>European Southern Observatory</common:name>
                        <common:disambiguated-organization>
                            <common:disambiguated-organization-identifier>grid.424907.c</common:disambiguated-organization-identifier>
                            <common:disambiguation-source>GRID</common:disambiguation-source>
                        </common:disambiguated-organization>
                    </common:organization>
                </employment:employment-summary>
            </activities:affiliation-group>
        </activities:employments>
    </activities:activities-summary>
</record:record>
"""

XML_ENTRY_DATA_SINGLE_EMPLOYMENT = b"""
<record:record>
    <common:orcid-identifier>
        <common:uri>https://orcid.org/0000-0001-8135-3489</common:uri>
        <common:path>0000-0001-8135-3489</common:path>
        <common:host>orcid.org</common:host>
    </common:orcid-identifier>
    <person:person>
        <person:name>
            <personal-details:given-names>Lars Holm</personal-details:given-names>
            <personal-details:family-name>Nielsen</personal-details:family-name>
        </person:name>
    </person:person>
    <activities:activities-summary>
        <activities:employments>
            <activities:affiliation-group>
                <employment:employment-summary>
                    <common:start-date>
                        <common:year>2012</common:year>
                        <common:month>03</common:month>
                        <common:day>16</common:day>
                    </common:start-date>
                    <common:organization>
                        <common:name>CERN</common:name>
                        <common:disambiguated-organization>
                            <common:disambiguated-organization-identifier>https://ror.org/01ggx4157
</common:disambiguated-organization-identifier>
                            <common:disambiguation-source>ROR</common:disambiguation-source>
                        </common:disambiguated-organization>
                    </common:organization>
                </employment:employment-summary>
            </activities:affiliation-group>
        </activities:employments>
    </activities:activities-summary>
</record:record>
"""


NAMES_TEST = {
    "Lars Holm, Nielsen": True,
    "Lars Nielsen:)": False,
    "Lars Nielsen-H": True,
    "Lars Nielsen 👍": False,
    "Lars Nielsen (CERN)": True,
}


@pytest.fixture(scope="function")
def orcid_data():
    base = {
        "orcid-identifier": {
            "uri": "https://orcid.org/0000-0001-8135-3489",
            "path": "0000-0001-8135-3489",
            "host": "orcid.org",
        },
        "person": {
            "name": {"given-names": "Lars Holm", "family-name": "Nielsen"},
        },
    }

    employments = [
        {
            "employment-summary": {
                "organization": {
                    "name": "CERN",
                    "disambiguated-organization": {
                        "disambiguated-organization-identifier": "https://ror.org/01ggx4157",
                        "disambiguation-source": "ROR",
                    },
                },
                "start-date": {"year": "2012", "month": "03", "day": "16"},
            }
        },
        {
            "employment-summary": {
                "organization": {
                    "name": "ACME Inc.",
                    "disambiguated-organization": {
                        "disambiguated-organization-identifier": "grid.123456.z",
                        "disambiguation-source": "GRID",
                    },
                },
                "start-date": {"year": "2024", "month": "01"},
            }
        },
        {
            "employment-summary": {
                "organization": {
                    "name": "European Southern Observatory",
                    "disambiguated-organization": {
                        "disambiguated-organization-identifier": "grid.424907.c",
                        "disambiguation-source": "GRID",
                    },
                },
                "start-date": {"year": "2007", "month": "08"},
                "end-date": {"year": "2012", "month": "03"},
            },
        },
    ]

    return {
        "xml": {
            "multi_employment": XML_ENTRY_DATA,
            "single_employment": XML_ENTRY_DATA_SINGLE_EMPLOYMENT,
        },
        "json": {
            "multi_employment": {
                **base,
                "activities-summary": {
                    "employments": {"affiliation-group": employments},
                },
            },
            "single_employment": {
                **base,
                "activities-summary": {
                    # NOTE: Because the XML data has only one employment, the
                    # transformer will not create a list of employments, but instead a
                    # single employment object.
                    "employments": {"affiliation-group": employments[0]}
                },
            },
            "duplicate_affiliations": {
                **base,
                "activities-summary": {
                    "employments": {"affiliation-group": employments + employments},
                },
            },
        },
    }


@pytest.fixture(scope="module")
def expected_from_xml():
    base = {
        "id": "0000-0001-8135-3489",
        "given_name": "Lars Holm",
        "family_name": "Nielsen",
        "identifiers": [{"scheme": "orcid", "identifier": "0000-0001-8135-3489"}],
    }

    return {
        "multi_employment": {
            **base,
            "affiliations": [
                {"id": "01ggx4157", "name": "CERN"},
                # NOTE: GRID identifiers do not result in linked affiliations
                {"name": "ACME Inc."},
                # NOTE: terminated employments are not included in the affiliations
            ],
        },
        "single_employment": {
            **base,
            "affiliations": [{"id": "01ggx4157", "name": "CERN"}],
        },
        "duplicate_affiliations": {
            **base,
            "affiliations": [
                # Affiliations are deduplicated
                {"id": "01ggx4157", "name": "CERN"},
                {"name": "ACME Inc."},
            ],
        },
    }


@pytest.fixture(scope="function")
def org_ids_mapping_file_config(app):
    """ORCiD organization IDs mappings CSV file."""
    fout = tempfile.NamedTemporaryFile(mode="w", delete=False)
    fout.write('"GRID","grid.123456.z","acme_inc_id"\n')
    fout.close()

    old_config = app.config.get("VOCABULARIES_ORCID_ORG_IDS_MAPPING_PATH")
    app.config["VOCABULARIES_ORCID_ORG_IDS_MAPPING_PATH"] = fout.name
    yield

    app.config["VOCABULARIES_ORCID_ORG_IDS_MAPPING_PATH"] = old_config
    os.unlink(fout.name)


def test_orcid_xml_transform(orcid_data):
    """Test XML transformer with ORCiD record.

    NOTE: this might look somewhat "redundant", since we're again testing if the
    XMLTransformer works as expected. However, this is a more specific test
    that demonstrates how the transformer behaves with more complex XML data, that
    can have e.g. nested elements that can be arrays or objects.
    """
    xml_data = orcid_data["xml"]
    json_data = orcid_data["json"]

    for key, data in xml_data.items():
        transformer = XMLTransformer(root_element="record")
        transform_result = transformer.apply(StreamEntry(data)).entry
        assert transform_result == json_data[key]


def test_orcid_transformer(app, orcid_data, expected_from_xml):
    """Test ORCiD transformer data."""
    transformer = OrcidTransformer()
    input_data = orcid_data["json"]

    for key, data in input_data.items():
        assert expected_from_xml[key] == transformer.apply(StreamEntry(data)).entry, key


def test_orcid_transformer_org_ids_mapping_from_file(
    app,
    orcid_data,
    expected_from_xml,
    org_ids_mapping_file_config,
):
    """Test ORCiD transformer data with org IDs mapping file."""
    transformer = OrcidTransformer()
    input_data = orcid_data["json"]["multi_employment"]
    expected = deepcopy(expected_from_xml["multi_employment"])
    expected["affiliations"] = [
        {"id": "01ggx4157", "name": "CERN"},
        {"id": "acme_inc_id", "name": "ACME Inc."},
    ]

    assert expected == transformer.apply(StreamEntry(input_data)).entry


@pytest.mark.parametrize("name,is_valid_name", NAMES_TEST.items())
def test_orcid_transformer_name_filtering(orcid_data, name, is_valid_name):
    transformer = OrcidTransformer()
    val = deepcopy(orcid_data["json"]["multi_employment"])
    if is_valid_name:
        assert transformer.apply(StreamEntry(val)).entry
    else:
        with pytest.raises(TransformerError):
            val["person"]["name"]["given-names"] = name
            val["person"]["name"]["family-name"] = ""
            transformer.apply(StreamEntry(val))
        with pytest.raises(TransformerError):
            val["person"]["name"]["given-names"] = ""
            val["person"]["name"]["family-name"] = name
            transformer.apply(StreamEntry(val))


@pytest.mark.parametrize("name", NAMES_TEST.keys())
def test_orcid_transformer_different_names_no_regex(orcid_data, name):
    transformer = OrcidTransformer(names_exclude_regex=None)
    val = deepcopy(orcid_data["json"]["multi_employment"])
    val["person"]["name"]["given-names"] = name
    val["person"]["name"]["family-name"] = ""
    assert transformer.apply(StreamEntry(val)).entry


class MockResponse:
    content = XML_ENTRY_DATA
    status_code = 200


@patch("requests.get", side_effect=lambda url, headers: MockResponse())
def test_orcid_http_reader(_):
    reader = OrcidHTTPReader(id="0000-0001-8135-3489")
    results = []
    for entry in reader.read():
        results.append(entry)

    assert len(results) == 1
    assert XML_ENTRY_DATA == results[0]


def test_names_service_writer_create(app, db, search_clear, name_full_data):
    writer = NamesServiceWriter()
    record = writer.write(StreamEntry(name_full_data))
    record = record.entry.to_dict()

    assert dict(record, **name_full_data) == record


def test_names_service_writer_duplicate(app, db, search_clear, name_full_data):
    writer = NamesServiceWriter()
    _ = writer.write(stream_entry=StreamEntry(name_full_data))
    Name.index.refresh()  # refresh index to make changes live
    with pytest.raises(WriterError) as err:
        writer.write(stream_entry=StreamEntry(name_full_data))

    expected_error = [f"Vocabulary entry already exists: {name_full_data}"]
    assert expected_error in err.value.args


def test_names_service_writer_update_existing(app, db, search_clear, name_full_data):
    # create vocabulary
    writer = NamesServiceWriter(update=True)
    name = writer.write(stream_entry=StreamEntry(name_full_data))
    Name.index.refresh()  # refresh index to make changes live
    # update vocabulary
    updated_name = deepcopy(name_full_data)
    updated_name["given_name"] = "Pablo"
    updated_name["family_name"] = "Panero"
    updated_name["name"] = "Panero, Pablo"
    # check changes vocabulary
    _ = writer.write(stream_entry=StreamEntry(updated_name))
    service = current_service_registry.get("names")
    record = service.read(system_identity, name.entry.id)
    record = record.to_dict()

    # needed while the writer resolves from ES
    assert _.entry.id == name.entry.id
    assert dict(record, **updated_name) == record


def test_names_service_writer_update_non_existing(
    app, db, search_clear, name_full_data
):
    # vocabulary item not created, call update directly
    updated_name = deepcopy(name_full_data)
    updated_name
    updated_name["given_name"] = "Pablo"
    updated_name["family_name"] = "Panero"
    updated_name["name"] = "Panero, Pablo"
    # check changes vocabulary
    writer = NamesServiceWriter(update=True)
    name = writer.write(stream_entry=StreamEntry(updated_name))
    service = current_service_registry.get("names")
    record = service.read(system_identity, name.entry.id)
    record = record.to_dict()

    assert dict(record, **updated_name) == record
