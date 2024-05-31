# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Data Streams readers tests."""
import json
import tarfile
import zipfile
from pathlib import Path

import pytest
import yaml

from invenio_vocabularies.datastreams.errors import ReaderError
from invenio_vocabularies.datastreams.readers import (
    JsonReader,
    OAIPMHReader,
    TarReader,
    YamlReader,
    ZipReader,
)


@pytest.fixture(scope="module")
def expected_from_yaml():
    return [{"test": {"inner": "value"}}, {"test": {"inner": "value"}}]


@pytest.fixture(scope="function")
def yaml_file(expected_from_yaml):
    filename = Path("reader_test.yaml")
    with open(filename, "w") as file:
        yaml.dump(expected_from_yaml, file)

    yield filename

    filename.unlink()  # delete created file


def test_yaml_reader(yaml_file, expected_from_yaml):
    reader = YamlReader(yaml_file)

    for idx, data in enumerate(reader.read()):
        assert data == expected_from_yaml[idx]


@pytest.fixture(scope="module")
def expected_from_tar():
    return {"test": {"inner": "value"}}


@pytest.fixture(scope="function")
def tar_file(expected_from_tar):
    """Creates a Tar file with three files (two yaml) inside.

    Each iteration should return the content of one yaml file,
    it should ignore the .other file.
    """
    files = ["file_one.yaml", "file_two.yaml", "file_three.other"]
    filename = Path("reader_test.tar.gz")
    with tarfile.open(filename, "w:gz") as tar:
        for file_ in files:
            inner_filename = Path(file_)
            with open(inner_filename, "w") as file:
                yaml.dump(expected_from_tar, file)
                tar.add(inner_filename)
            inner_filename.unlink()

    yield filename

    filename.unlink()  # delete created file


def test_tar_reader(tar_file, expected_from_tar):
    reader = TarReader(tar_file, regex=".yaml$")

    total = 0
    for data in reader.read():
        assert yaml.safe_load(data) == expected_from_tar
        total += 1

    assert total == 2  # ignored the `.other` file


def test_zip_reader(zip_file, json_list):
    reader = ZipReader(zip_file, regex=".json$")
    total = 0
    for data in reader.read():
        assert json.load(data) == json_list
        total += 1

    assert total == 2  # ignored the `.other` file


def test_zip_reader_item_zipfile_instance(zip_file, json_list):
    reader = ZipReader(regex=".json$")
    total = 0
    with zipfile.ZipFile(zip_file) as archive:
        for data in reader.read(archive):
            assert json.load(data) == json_list
            total += 1

    assert total == 2  # ignored the `.other` file


def test_zip_reader_item_filename_not_zipfile_instance(zip_file, json_list):
    reader = ZipReader(regex=".json$")
    total = 0
    for data in reader.read(zip_file):
        assert json.load(data) == json_list
        total += 1

    assert total == 2  # ignored the `.other` file


@pytest.fixture(scope="function")
def json_list_file(json_list):
    """Creates a JSON file with an array inside."""
    filename = Path("reader_test.json")
    with open(filename, mode="w") as file:
        json.dump(json_list, file)

    yield filename

    filename.unlink()  # delete created file


def test_json_list_reader(json_list_file, json_element):
    reader = JsonReader(json_list_file, regex=".json$")

    for count, data in enumerate(reader.read(), start=1):
        assert data == json_element

    assert count == 2


@pytest.fixture(scope="function")
def json_element_file(json_element):
    """Creates a JSON file with only one element inside."""
    filename = Path("reader_test.json")
    with open(filename, mode="w") as file:
        json.dump(json_element, file)
    yield filename
    filename.unlink()  # delete created file


def test_json_element_reader(json_element_file, json_element):
    reader = JsonReader(json_element_file, regex=".json$")

    for count, data in enumerate(reader.read(), start=1):
        assert data == json_element

    assert count == 1


@pytest.fixture(scope="module")
def oai_response_match():
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
    return response_data


def test_oaipmh_reader(app, httpserver, oai_response_match):
    httpserver.expect_request("/oai/repository").respond_with_data(
        response_data=oai_response_match, mimetype="application/xml"
    )
    reader = OAIPMHReader(
        base_url=httpserver.url_for("/oai/repository"),
        metadata_prefix="MARC21plus-1-xml",
        set="authorities:sachbegriff",
        from_date="2024-01-01T09:00:00Z",
        until_date="2024-01-31T10:00:00Z",
    )
    result = reader.read()
    assert "record" in next(result)


@pytest.fixture(scope="module")
def oai_response_no_match():
    response_data = """
        <OAI-PMH xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd" xmlns="http://www.openarchives.org/OAI/2.0/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            <responseDate>2024-05-29T13:09:44Z</responseDate>
            <request metadataPrefix="MARC21plus-1-xml" set="authorities:sachbegriff" verb="ListRecords" from="2024-01-01T09:00:00Z" until="2024-01-01T10:00:00Z">https://services.dnb.de/oai/repository</request>
            <error code="noRecordsMatch"/>
        </OAI-PMH>
    """
    return response_data


def test_oaipmh_reader_no_records_match(httpserver, oai_response_no_match):
    httpserver.expect_request("/oai/repository").respond_with_data(
        response_data=oai_response_no_match, mimetype="application/xml"
    )
    reader = OAIPMHReader(
        base_url=httpserver.url_for("/oai/repository"),
        metadata_prefix="MARC21plus-1-xml",
        set="authorities:sachbegriff",
        from_date="2024-01-01T09:00:00Z",
        until_date="2024-01-01T10:00:00Z",
    )
    result = reader.read()
    with pytest.raises(ReaderError):
        next(result)


# FIXME: add test for csv reader
