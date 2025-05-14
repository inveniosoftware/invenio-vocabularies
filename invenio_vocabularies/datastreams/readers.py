# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 CERN.
# Copyright (C)      2024 University of Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Readers module."""

import csv
import gzip
import io
import json
import re
import tarfile
import zipfile
from abc import ABC, abstractmethod
from json.decoder import JSONDecodeError

import requests
import yaml
from lxml import etree
from lxml.html import fromstring
from lxml.html import parse as html_parse

from .errors import ReaderError
from .xml import etree_to_dict

# Extras dependencies
# "oaipmh"
try:
    import oaipmh_scythe
except ImportError:
    oaipmh_scythe = None

# "rdf"
try:
    import rdflib
except ImportError:
    rdflib = None

# "sparql"
try:
    import SPARQLWrapper as sparql
except ImportError:
    sparql = None


class BaseReader(ABC):
    """Base reader."""

    def __init__(self, origin=None, mode="r", *args, **kwargs):
        """Constructor.

        :param origin: Data source (e.g. filepath).
                       Can be none in case of piped readers.
        """
        self._origin = origin
        self._mode = mode

    @abstractmethod
    def _iter(self, fp, *args, **kwargs):
        """Yields data objects file pointer."""
        pass

    def read(self, item=None, *args, **kwargs):
        """Reads from item or opens the file descriptor from origin."""
        if item:
            yield from self._iter(fp=item, *args, **kwargs)
        else:
            with open(self._origin, self._mode) as file:
                yield from self._iter(fp=file, *args, **kwargs)


class YamlReader(BaseReader):
    """Yaml reader."""

    def _iter(self, fp, *args, **kwargs):
        """Reads a yaml file and returns a dictionary per element."""
        data = yaml.safe_load(fp) or []
        for entry in data:
            yield entry


class TarReader(BaseReader):
    """Tar reader."""

    def __init__(self, *args, mode="r|gz", regex=None, **kwargs):
        """Constructor."""
        self._regex = re.compile(regex) if regex else None
        super().__init__(*args, mode=mode, **kwargs)

    def _iter(self, fp, *args, **kwargs):
        """Iterates through the files in the archive."""
        for member in fp:
            match = not self._regex or self._regex.search(member.name)
            if member.isfile() and match:
                yield fp.extractfile(member)

    def read(self, item=None, *args, **kwargs):
        """Opens a tar archive or uses the given file pointer."""
        if item:
            if isinstance(item, tarfile.TarFile):
                yield from self._iter(fp=item, *args, **kwargs)
            else:
                # If the item is not already a TarFile (e.g. if it is a BytesIO), try to create a TarFile from the item.
                with tarfile.open(mode=self._mode, fileobj=item) as archive:
                    yield from self._iter(fp=archive, *args, **kwargs)
        else:
            with tarfile.open(self._origin, self._mode) as archive:
                yield from self._iter(fp=archive, *args, **kwargs)


class SimpleHTTPReader(BaseReader):
    """Simple HTTP Reader."""

    def __init__(self, origin, id=None, ids=None, content_type=None, *args, **kwargs):
        """Constructor."""
        self._ids = ids if ids else ([id] if id else None)
        self.content_type = content_type
        super().__init__(origin, *args, **kwargs)

    def _iter(self, url, *args, **kwargs):
        """Queries an URL."""
        base_url = url
        headers = {"Accept": self.content_type}

        # If there are no IDs, query the base URL
        if not self._ids:
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                yield resp.content
            else:
                print(f"Failed to fetch URL {url}: {resp.status_code}")
        else:
            for id_ in self._ids:
                url = base_url.format(id=id_)
                resp = requests.get(url, headers=headers)
                if resp.status_code != 200:
                    # todo add logging/fail
                    pass

                yield resp.content

    def read(self, item=None, *args, **kwargs):
        """Chooses between item and origin as url."""
        url = item if item else self._origin
        yield from self._iter(url=url, *args, **kwargs)


class ZipReader(BaseReader):
    """ZIP reader."""

    def __init__(self, *args, options=None, regex=None, **kwargs):
        """Constructor."""
        self._options = options or {}
        self._regex = re.compile(regex) if regex else None
        super().__init__(*args, **kwargs)

    def _iter(self, fp, *args, **kwargs):
        """Iterates through the files in the archive."""
        for member in fp.infolist():
            match = not self._regex or self._regex.search(member.filename)
            if not member.is_dir() and match:
                yield fp.open(member)

    def read(self, item=None, *args, **kwargs):
        """Opens a Zip archive or uses the given file pointer."""
        # https://docs.python.org/3/library/zipfile.html
        if item:
            if isinstance(item, zipfile.ZipFile):
                yield from self._iter(fp=item, *args, **kwargs)
            else:
                # If the item is not already a ZipFile (e.g. if it is a BytesIO), try to create a ZipFile from the item.
                with zipfile.ZipFile(item, **self._options) as archive:
                    yield from self._iter(fp=archive, *args, **kwargs)
        else:
            with zipfile.ZipFile(self._origin, **self._options) as archive:
                yield from self._iter(fp=archive, *args, **kwargs)


class JsonReader(BaseReader):
    """JSON object reader."""

    def _iter(self, fp, *args, **kwargs):
        """Reads (loads) a json object and yields its items."""
        try:
            entries = json.load(fp)
            if isinstance(entries, list):
                for entry in entries:
                    yield entry
            else:
                yield entries  # just one entry
        except JSONDecodeError as err:
            raise ReaderError(f"Cannot decode JSON file {fp.name}: {str(err)}")


class JsonLinesReader(BaseReader):
    """JSON Lines reader."""

    def _iter(self, fp, *args, **kwargs):
        for idx, line in enumerate(fp):
            try:
                data = json.loads(line)
                if isinstance(data, list):
                    for entry in data:
                        yield entry
                else:
                    yield data  # just one entry
            except JSONDecodeError as err:
                raise ReaderError(
                    f"Cannot decode JSON line {fp.name}:{idx}: {str(err)}"
                )


class GzipReader(BaseReader):
    """Gzip reader."""

    def _iter(self, fp, *args, **kwargs):
        if isinstance(fp, bytes):
            fp = io.BytesIO(fp)

        with gzip.open(fp) as gp:
            yield gp


class CSVReader(BaseReader):
    """Reads a CSV file and returns a dictionary per element."""

    def __init__(self, *args, csv_options=None, as_dict=True, **kwargs):
        """Constructor."""
        self.csv_options = csv_options or {}
        self.as_dict = as_dict
        super().__init__(*args, **kwargs)

    def _iter(self, fp, *args, **kwargs):
        """Reads a csv file and returns a dictionary per element."""
        csvfile = fp
        if self.as_dict:
            reader = csv.DictReader(csvfile, **self.csv_options)
        else:
            reader = csv.reader(csvfile, **self.csv_options)
        for row in reader:
            yield row


class XMLReader(BaseReader):
    """XML reader."""

    def __init__(self, root_element=None, *args, **kwargs):
        """Constructor."""
        self.root_element = root_element
        super().__init__(*args, **kwargs)

    def _iter(self, fp, *args, **kwargs):
        """Read and parse an XML file to dict."""
        # NOTE: We parse HTML, to skip XML validation and strip XML namespaces
        record = None
        try:
            xml_tree = fromstring(fp)
            xml_dict = etree_to_dict(xml_tree)
        except Exception:
            xml_tree = html_parse(fp).getroot()
            xml_dict = etree_to_dict(xml_tree)["html"]["body"]

        if self.root_element:
            record = xml_dict.get(self.root_element)
            if not record:
                raise ReaderError(
                    f"Root element '{self.root_element}' not found in XML entry."
                )
        else:
            record = xml_dict

        yield record


class OAIPMHReader(BaseReader):
    """OAIPMH reader."""

    def __init__(
        self,
        *args,
        base_url=None,
        metadata_prefix=None,
        set=None,
        from_date=None,
        until_date=None,
        verb=None,
        **kwargs,
    ):
        """Constructor."""
        self._base_url = base_url
        self._metadata_prefix = metadata_prefix if not None else "oai_dc"
        self._set = set
        self._until = until_date
        self._from = from_date
        self._verb = verb if not None else "ListRecords"
        super().__init__(*args, **kwargs)

    def _iter(self, scythe, *args, **kwargs):
        """Read and parse an OAIPMH stream to dict."""

        class OAIRecord(oaipmh_scythe.models.Record):
            """An XML unpacking implementation for more complicated formats."""

            def get_metadata(self):
                """Extract and return the record's metadata as a dictionary."""
                return xml_to_dict(
                    self.xml.find(f".//{self._oai_namespace}metadata").getchildren()[0],
                )

        if self._verb == "ListRecords":
            scythe.class_mapping["ListRecords"] = OAIRecord
            try:
                records = scythe.list_records(
                    from_=self._from,
                    until=self._until,
                    metadata_prefix=self._metadata_prefix,
                    set_=self._set,
                    ignore_deleted=True,
                )
                for record in records:
                    yield {"record": record}
            except oaipmh_scythe.NoRecordsMatch:
                raise ReaderError("No records found in OAI-PMH request.")
        else:
            scythe.class_mapping["GetRecord"] = OAIRecord
            try:
                headers = scythe.list_identifiers(
                    from_=self._from,
                    until=self._until,
                    metadata_prefix=self._metadata_prefix,
                    set_=self._set,
                    ignore_deleted=True,
                )
                for header in headers:
                    record = scythe.get_record(
                        identifier=header.identifier,
                        metadata_prefix=self._metadata_prefix,
                    )
                    yield {"record": record}
            except oaipmh_scythe.NoRecordsMatch:
                raise ReaderError("No records found in OAI-PMH request.")

    def read(self, item=None, *args, **kwargs):
        """Reads from item or opens the file descriptor from origin."""
        if item:
            raise NotImplementedError(
                "OAIPMHReader does not support being chained after another reader"
            )
        else:
            with oaipmh_scythe.Scythe(self._base_url) as scythe:
                yield from self._iter(scythe=scythe, *args, **kwargs)


def xml_to_dict(tree: etree._Element):
    """Convert an XML tree to a dictionary.

    This function takes an XML element tree and converts it into a dictionary.

    Args:
        tree: The root element of the XML tree to be converted.

    Returns:
        A dictionary with the key "record".
    """
    dict_obj = dict()
    dict_obj["record"] = etree.tostring(tree)

    return dict_obj


class RDFReader(BaseReader):
    """Base Reader class to fetch and process RDF data."""

    @property
    def skos_core(self):
        """Return the SKOS Core namespace."""
        return rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")

    def _iter(self, rdf_graph):
        """Iterate over the RDF graph, yielding one subject at a time."""
        for subject, _, _ in rdf_graph.triples(
            (None, rdflib.RDF.type, self.skos_core.Concept)
        ):
            yield {"subject": subject, "rdf_graph": rdf_graph}

    def read(self, item=None, *args, **kwargs):
        """Fetch and process the RDF data, yielding it one subject at a time."""
        if isinstance(item, gzip.GzipFile):
            rdf_content = item.read().decode("utf-8")

        elif isinstance(item, bytes):
            rdf_content = item.decode("utf-8")
        else:
            raise ReaderError("Unsupported content type")

        rdf_graph = rdflib.Graph()
        rdf_graph.parse(io.StringIO(rdf_content), format="xml")

        yield from self._iter(rdf_graph)


class SPARQLReader(BaseReader):
    """Generic reader class to fetch and process RDF data from a SPARQL endpoint."""

    def __init__(self, origin, query, mode="r", client_params=None, *args, **kwargs):
        """Initialize the reader with the data source.

        :param origin: The SPARQL endpoint from which to fetch the RDF data.
        :param query: The SPARQL query to execute.
        :param mode: Mode of operation (default is 'r' for reading).
        :param client_params: Additional client parameters to pass to the SPARQL client.
        """
        self._origin = origin
        self._query = query
        self._client_params = client_params or {}

        super().__init__(origin=origin, mode=mode, *args, **kwargs)

    def _iter(self, fp, *args, **kwargs):
        raise NotImplementedError(
            "SPARQLReader downloads one result set from SPARQL and therefore does not iterate through items"
        )

    def read(self, item=None, *args, **kwargs):
        """Fetch and process RDF data, yielding results one at a time."""
        if item:
            raise NotImplementedError(
                "SPARQLReader does not support being chained after another reader"
            )

        # Avoid overwriting SPARQLWrapper's default value for the user agent string
        if self._client_params.get("user_agent"):
            sparql_client = sparql.SPARQLWrapper(
                self._origin, agent=self._client_params.get("user_agent")
            )
        else:
            sparql_client = sparql.SPARQLWrapper(self._origin)

        sparql_client.setQuery(self._query)
        sparql_client.setReturnFormat(sparql.JSON)

        results = sparql_client.query().convert()
        yield from results["results"]["bindings"]
