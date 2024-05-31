# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""DataStreams tests."""

import json
import zipfile
from pathlib import Path

import pytest
from pytest_httpserver import httpserver

from invenio_vocabularies.datastreams.errors import ReaderError
from invenio_vocabularies.datastreams.factories import DataStreamFactory


@pytest.fixture(scope="module")
def vocabulary_config():
    """Parsed vocabulary configuration."""
    return {
        "transformers": [{"type": "test"}],
        "readers": [
            {
                "type": "test",
                "args": {
                    "origin": [1, -1],
                },
            }
        ],
        "writers": [{"type": "test"}],
    }


def test_base_datastream(app, vocabulary_config):
    datastream = DataStreamFactory.create(
        readers_config=vocabulary_config["readers"],
        transformers_config=vocabulary_config.get("transformers"),
        writers_config=vocabulary_config["writers"],
    )

    stream_iter = datastream.process()
    valid = next(stream_iter)
    assert valid.entry == 2
    assert not valid.errors

    invalid = next(stream_iter)
    assert invalid.entry == -1
    assert "TestTransformer: Value cannot be negative" in invalid.errors


def test_base_datastream_fail_on_write(app, vocabulary_config):
    custom_config = dict(vocabulary_config)
    custom_config["writers"].append(
        {
            "type": "fail",
            "args": {"fail_on": 2},  # 2 means 1 as entry cuz transformers sums 1
        }
    )

    datastream = DataStreamFactory.create(
        readers_config=vocabulary_config["readers"],
        transformers_config=vocabulary_config.get("transformers"),
        writers_config=vocabulary_config["writers"],
    )

    stream_iter = datastream.process()
    invalid_wr = next(stream_iter)
    assert invalid_wr.entry == 2  # entry got transformed
    assert "FailingTestWriter: 2 value found." in invalid_wr.errors

    # failed on the previous but can process the next
    invalid_tr = next(stream_iter)
    assert invalid_tr.entry == -1
    assert "TestTransformer: Value cannot be negative" in invalid_tr.errors


@pytest.fixture(scope="function")
def zip_file(json_list):
    """Creates a Zip file with three files inside.

    The first file should return two json elements.
    The second file should fail.
    The third file should return two json elements.
    """

    def _correct_file(archive, idx):
        correct_file = Path(f"correct_{idx}.json")
        with open(correct_file, "w") as file:
            json.dump(json_list, file)
        archive.write(correct_file)
        correct_file.unlink()

    filename = Path("reader_test.zip")
    with zipfile.ZipFile(file=filename, mode="w") as archive:
        _correct_file(archive, 1)
        errored_file = Path("errored.json")
        with open(errored_file, "w") as file:
            file.write(  # to dump incorrect json format
                # missing comma and closing bracket
                '[{"test": {"inner": "value"}{"test": {"inner": "value"}}]'
            )
        archive.write(errored_file)
        _correct_file(archive, 2)
        errored_file.unlink()

    yield filename

    filename.unlink()  # delete created file


def test_piping_readers(app, zip_file, json_element):
    ds_config = {
        "readers": [
            {
                "type": "zip",
                "args": {
                    "origin": "reader_test.zip",
                    "regex": "\\.json$",
                },
            },
            {"type": "json"},
        ],
        "writers": [{"type": "test"}],
    }

    datastream = DataStreamFactory.create(
        readers_config=ds_config["readers"],
        writers_config=ds_config["writers"],
    )
    expected_errors = [
        "ZipReader.read: Cannot decode JSON file errored.json: Expecting ',' delimiter: line 1 column 29 (char 28)"  # noqa
    ]

    iter = datastream.process()
    for count, entry in enumerate(iter, start=1):
        if count != 3:
            assert entry.entry == json_element
        else:
            # assert the second file fails
            assert entry.entry.name == "errored.json"
            assert entry.errors == expected_errors

    assert count == 5  # 2 good + 1 bad + 2 good


def test_oaipmh_reader(app, httpserver):
    response_data = """
        <?xml version = "1.0" encoding = "UTF-8"?>
        <OAI-PMH xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd" xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <responseDate>2024-05-29T13:20:04Z</responseDate>
            <request metadataPrefix="MARC21plus-1-xml" set="authorities:sachbegriff" verb="ListRecords" from="2024-01-01T09:00:00Z" until="2024-01-01T17:00:00Z">https://services.dnb.de/oai/repository</request>
            <ListRecords xsi:schemaLocation="http://www.loc.gov/MARC21/slim http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd">
                <record>
                    <header>
                        <identifier>oai:dnb.de/authorities:sachbegriff/1074025261</identifier>
                        <datestamp>2024-01-01T16:51:21Z</datestamp>
                        <setSpec>authorities:sachbegriff</setSpec>
                    </header>
                    <metadata>
                        <record type="Authority" xmlns="http://www.loc.gov/MARC21/slim">
                            <leader>00000nz  a2200000nc 4500</leader>
                            <controlfield tag="001">1074025261</controlfield>
                            <controlfield tag="003">DE-101</controlfield>
                            <controlfield tag="005">20240101175121.0</controlfield>
                            <controlfield tag="008">150717n||azznnbabn           | ana    |c</controlfield>
                            <datafield tag="024" ind1="7" ind2=" ">
                                <subfield code="a">1074025261</subfield>
                                <subfield code="0">http://d-nb.info/gnd/1074025261</subfield>
                                <subfield code="2">gnd</subfield>
                            </datafield>
                            <datafield tag="035" ind1=" " ind2=" ">
                                <subfield code="a">(DE-101)1074025261</subfield>
                            </datafield>
                            <datafield tag="035" ind1=" " ind2=" ">
                                <subfield code="a">(DE-588)1074025261</subfield>
                            </datafield>
                            <datafield tag="040" ind1=" " ind2=" ">
                                <subfield code="a">DE-12</subfield>
                                <subfield code="c">DE-12</subfield>
                                <subfield code="9">r:DE-384</subfield>
                                <subfield code="b">ger</subfield>
                                <subfield code="d">1210</subfield>
                                <subfield code="f">rswk</subfield>
                            </datafield>
                            <datafield tag="042" ind1=" " ind2=" ">
                                <subfield code="a">gnd1</subfield>
                            </datafield>
                            <datafield tag="065" ind1=" " ind2=" ">
                                <subfield code="a">31.3b</subfield>
                                <subfield code="2">sswd</subfield>
                            </datafield>
                            <datafield tag="075" ind1=" " ind2=" ">
                                <subfield code="b">s</subfield>
                                <subfield code="2">gndgen</subfield>
                            </datafield>
                            <datafield tag="075" ind1=" " ind2=" ">
                                <subfield code="b">saz</subfield>
                                <subfield code="2">gndspec</subfield>
                            </datafield>
                            <datafield tag="079" ind1=" " ind2=" ">
                                <subfield code="a">g</subfield>
                                <subfield code="q">s</subfield>
                            </datafield>
                            <datafield tag="150" ind1=" " ind2=" ">
                                <subfield code="a">Rundbogenhalle</subfield>
                            </datafield>
                            <datafield tag="450" ind1=" " ind2=" ">
                                <subfield code="a">Bogenhalle</subfield>
                            </datafield>
                            <datafield tag="550" ind1=" " ind2=" ">
                                <subfield code="0">(DE-101)040230236</subfield>
                                <subfield code="0">(DE-588)4023023-5</subfield>
                                <subfield code="0">https://d-nb.info/gnd/4023023-5</subfield>
                                <subfield code="a">Halle</subfield>
                                <subfield code="4">obge</subfield>
                                <subfield code="4">https://d-nb.info/standards/elementset/gnd#broaderTermGeneric</subfield>
                                <subfield code="w">r</subfield>
                                <subfield code="i">Oberbegriff generisch</subfield>
                            </datafield>
                            <datafield tag="670" ind1=" " ind2=" ">
                                <subfield code="a">Stahlbetonbauwerke mit großer Spannweite, eingesetzt im Industriebau, z.b.Paketposthalle München; teilweise heute unter Denkmalschutz</subfield>
                            </datafield>
                        </record>
                    </metadata>
                </record>
            </ ListRecords>
        </OAI-PMH>
    """
    httpserver.expect_request("/oai/repository").respond_with_data(
        response_data=response_data, mimetype="application/xml"
    )
    ds_config = {
        "readers": [
            {
                "type": "oai-pmh",
                "args": {
                    "base_url": httpserver.url_for("/oai/repository"),
                    "metadata_prefix": "MARC21plus-1-xml",
                    "set": "authorities:sachbegriff",
                    "from_date": "2024-01-01T09:00:00Z",
                    "until_date": "2024-01-31T10:00:00Z",
                },
            },
        ],
        "writers": [{"type": "test"}],
    }

    datastream = DataStreamFactory.create(
        readers_config=ds_config["readers"],
        writers_config=ds_config["writers"],
    )
    iter = datastream.process()
    for count, entry in enumerate(iter, start=1):
        assert "record" in entry.entry
        break


def test_oaipmh_reader_no_records_match(app, httpserver):
    response_data = """
        <OAI-PMH xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd" xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <responseDate>2024-05-29T13:09:44Z</responseDate>
            <request metadataPrefix="MARC21plus-1-xml" set="authorities:sachbegriff" verb="ListRecords" from="2024-01-01T09:00:00Z" until="2024-01-01T10:00:00Z">https://services.dnb.de/oai/repository</request>
            <error code="noRecordsMatch"/>
        </OAI-PMH>
    """
    httpserver.expect_request("/oai/repository").respond_with_data(
        response_data=response_data, mimetype="application/xml"
    )
    ds_config = {
        "readers": [
            {
                "type": "oai-pmh",
                "args": {
                    "base_url": httpserver.url_for("/oai/repository"),
                    "metadata_prefix": "MARC21plus-1-xml",
                    "set": "authorities:sachbegriff",
                    "from_date": "2024-01-01T09:00:00Z",
                    "until_date": "2024-01-01T10:00:00Z",
                },
            },
        ],
        "writers": [{"type": "test"}],
    }

    datastream = DataStreamFactory.create(
        readers_config=ds_config["readers"],
        writers_config=ds_config["writers"],
    )
    stream_iter = datastream.process()
    with pytest.raises(ReaderError):
        next(stream_iter)
