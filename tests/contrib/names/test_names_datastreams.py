# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names data streams tests."""

from unittest.mock import patch

import pytest

from invenio_vocabularies.contrib.names.datastreams import OrcidHTTPReader, \
    OrcidXMLTransformer
from invenio_vocabularies.datastreams import StreamEntry


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


@pytest.fixture(scope='module')
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
