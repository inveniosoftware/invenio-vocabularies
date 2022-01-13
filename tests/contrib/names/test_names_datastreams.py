# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names data streams tests."""

from copy import deepcopy
from unittest.mock import patch

import pytest
from invenio_access.permissions import system_identity

from invenio_vocabularies.contrib.names.api import Name
from invenio_vocabularies.contrib.names.datastreams import \
    NamesServiceWriter, OrcidHTTPReader, OrcidXMLTransformer
from invenio_vocabularies.contrib.names.services import NamesService, \
    NamesServiceConfig
from invenio_vocabularies.datastreams import StreamEntry
from invenio_vocabularies.datastreams.errors import WriterError


@pytest.fixture(scope='module')
def names_service():
    """Names service object."""
    return NamesService(config=NamesServiceConfig)


@pytest.fixture(scope="module")
def extra_entry_points():
    """Extra entry points to load the mock_module features."""
    return {
        'invenio_db.model': [
            'names = invenio_vocabularies.contrib.names.models',
        ],
        'invenio_jsonschemas.schemas': [
            'names = invenio_vocabularies.contrib.names.jsonschemas',
        ],
        'invenio_search.mappings': [
            'names = invenio_vocabularies.contrib.names.mappings',
        ]
    }


@pytest.fixture(scope="module")
def base_app(base_app, names_service):
    """Application factory fixture."""
    registry = base_app.extensions['invenio-records-resources'].registry
    registry.register(names_service, service_id='rdm-names')

    yield base_app


@pytest.fixture(scope="function")
def name_full_data():
    """Full name data."""
    return {
        'given_name': 'Lars Holm',
        'family_name': 'Nielsen',
        'identifiers': [
            {
                'scheme': 'orcid',
                'identifier': '0000-0001-8135-3489'  # normalized after create
            }
        ],
        'affiliations': [{'name': 'CERN'}]
    }


@pytest.fixture(scope='module')
def expected_from_xml():
    return {
        'given_name': 'Lars Holm',
        'family_name': 'Nielsen',
        'identifiers': [
            {
                'scheme': 'orcid',
                'identifier': 'https://orcid.org/0000-0001-8135-3489'
            }
        ],
        'affiliations': [{'name': 'CERN'}]
    }


XML_ENTRY_DATA = bytes(
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<record:record path="/0000-0001-8135-3489">\n'
        '    <common:orcid-identifier>\n'
        '        <common:uri>https://orcid.org/0000-0001-8135-3489</common:uri>\n'  # noqa
        '        <common:path>0000-0001-8135-3489</common:path>\n'
        '        <common:host>orcid.org</common:host>\n'
        '    </common:orcid-identifier>\n'
        '    <person:person path="/0000-0001-8135-3489/person">\n'
        '        <person:name visibility="public" path="0000-0001-8135-3489">\n'  # noqa
        '            <personal-details:given-names>Lars Holm</personal-details:given-names>'  # noqa
        '            <personal-details:family-name>Nielsen</personal-details:family-name>\n'  # noqa
        '        </person:name>\n'
        '        <external-identifier:external-identifiers path="/0000-0001-8135-3489/external-identifiers"/>\n'  # noqa
        '    </person:person>\n'
        '    <activities:activities-summary path="/0000-0001-8135-3489/activities">\n'  # noqa
        '       <activities:employments path="/0000-0001-8135-3489/employments">\n'  # noqa
        '           <employments:affiliation-group>\n'
        '               <employments:employment-summary>\n'
        '                   <employment-summary:organization>\n'
        '                       <organization:name>CERN</organization:name>\n'
        '                   </employment-summary:organization>\n'
        '               </employments:employment-summary>\n'
        '           </employments:affiliation-group>\n'
        '       </activities:employments>\n'
        '    </activities:activities-summary>\n'
        '</record:record>\n',
        encoding="raw_unicode_escape"
    )


@pytest.fixture(scope='function')
def bytes_xml_entry():
    # simplified version of an XML file of the ORCiD dump
    return StreamEntry(XML_ENTRY_DATA)


def test_orcid_xml_transformer(bytes_xml_entry, expected_from_xml):
    transformer = OrcidXMLTransformer()
    assert expected_from_xml == transformer.apply(bytes_xml_entry).entry


class MockResponse():
    content = XML_ENTRY_DATA
    status_code = 200


@patch('requests.get', side_effect=lambda url, headers: MockResponse())
def test_orcid_http_reader(_, bytes_xml_entry):
    reader = OrcidHTTPReader(id="0000-0001-8135-3489")
    results = []
    for entry in reader.read():
        results.append(entry)

    assert len(results) == 1
    assert bytes_xml_entry.entry == results[0].entry
    assert not results[0].errors


def test_names_service_writer_create(app, es_clear, name_full_data):
    writer = NamesServiceWriter("rdm-names", system_identity)
    record = writer.write(StreamEntry(name_full_data))
    record = record.entry.to_dict()

    assert dict(record, **name_full_data) == record


def test_names_service_writer_duplicate(app, es_clear, name_full_data):
    writer = NamesServiceWriter("rdm-names", system_identity)
    _ = writer.write(stream_entry=StreamEntry(name_full_data))
    Name.index.refresh()  # refresh index to make changes live
    with pytest.raises(WriterError) as err:
        writer.write(stream_entry=StreamEntry(name_full_data))

    expected_error = [f"Vocabulary entry already exists: {name_full_data}"]
    assert expected_error in err.value.args


def test_names_service_writer_update_existing(
    app, es_clear, name_full_data, names_service
):
    # create vocabulary
    writer = NamesServiceWriter("rdm-names", system_identity, update=True)
    name = writer.write(stream_entry=StreamEntry(name_full_data))
    Name.index.refresh()  # refresh index to make changes live
    # update vocabulary
    updated_name = deepcopy(name_full_data)
    updated_name["given_name"] = "Pablo"
    updated_name["family_name"] = "Panero"
    # check changes vocabulary
    _ = writer.write(stream_entry=StreamEntry(updated_name))
    record = names_service.read(system_identity, name.entry.id)
    record = record.to_dict()

    # needed while the writer resolves from ES
    assert _.entry.id == name.entry.id
    assert dict(record, **updated_name) == record


def test_names_service_writer_update_non_existing(
    app, es_clear, name_full_data, names_service
):
    # vocabulary item not created, call update directly
    updated_name = deepcopy(name_full_data)
    updated_name["given_name"] = "Pablo"
    updated_name["family_name"] = "Panero"
    # check changes vocabulary
    writer = NamesServiceWriter("rdm-names", system_identity, update=True)
    name = writer.write(stream_entry=StreamEntry(updated_name))
    record = names_service.read(system_identity, name.entry.id)
    record = record.to_dict()

    assert dict(record, **updated_name) == record
