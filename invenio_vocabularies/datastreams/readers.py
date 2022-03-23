# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Readers module."""

import csv
import json
import re
import tarfile
import zipfile
from abc import ABC, abstractmethod
from json.decoder import JSONDecodeError

import requests
import yaml

from .errors import ReaderError


class BaseReader(ABC):
    """Base reader."""

    def __init__(self, origin=None, *args, **kwargs):
        """Constructor.

        :param origin: Data source (e.g. filepath).
                       Can be none in case of piped readers.
        """
        self._origin = origin

    @abstractmethod
    def read(self, item=None, *args, **kwargs):
        """Reads the content from the origin.

        Yields data objects.
        """
        pass


class YamlReader(BaseReader):
    """Yaml reader."""

    def read(self, item=None):
        """Reads a yaml file and returns a dictionary per element."""
        file = item if item else open(self._origin, mode='r')

        data = yaml.safe_load(file) or []
        for entry in data:
            yield entry

        file.close()


class TarReader(BaseReader):
    """Tar reader."""

    def __init__(self, *args, mode="r|gz", regex=None, **kwargs):
        """Constructor."""
        self._regex = re.compile(regex) if regex else None
        self._mode = mode
        super().__init__(*args, **kwargs)

    def read(self, item=None):
        """Opens a tar and iterates through the files in the archive."""
        filepath = item or self._origin
        with tarfile.open(filepath, self._mode) as archive:
            for member in archive:
                match = not self._regex or self._regex.search(member.name)
                if member.isfile() and match:
                    content = archive.extractfile(member).read()
                    yield content


class SimpleHTTPReader(BaseReader):
    """Simple HTTP Reader."""

    def __init__(
        self, origin, id=None, ids=None, content_type=None, *args, **kwargs
    ):
        """Constructor."""
        assert id or ids
        self._ids = ids if ids else [id]
        self.content_type = content_type
        super().__init__(origin, *args, **kwargs)

    def read(self):
        """Reads a yaml file and returns a dictionary per element."""
        headers = {"Accept": self.content_type}

        for id_ in self._ids:
            url = self._origin.format(id=id_)
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                # todo add logging/fail
                pass

            yield resp.content


class ZipReader(BaseReader):
    """ZIP reader."""

    def __init__(self, *args, options=None, regex=None, **kwargs):
        """Constructor."""
        self._options = options or {}
        self._regex = re.compile(regex) if regex else None
        super().__init__(*args, **kwargs)

    def read(self, item=None):
        """Opens a ZIP and iterates through the files in the archive."""
        # https://docs.python.org/3/library/zipfile.html
        filepath = item or self._origin
        with zipfile.ZipFile(filepath, **self._options) as archive:
            for member in archive.infolist():
                match = not self._regex or self._regex.search(member.filename)
                if not member.is_dir() and match:
                    yield archive.open(member)


class JsonReader(BaseReader):
    """JSON object reader."""

    def read(self, item=None, **kwargs):
        """Reads (loads) a json object and yields its items."""
        def _read(file):
            try:
                entries = json.load(file)
                for entry in entries:
                    yield entry
            except JSONDecodeError as err:
                raise ReaderError(
                    f"Cannot decode JSON file {file.name}: {str(err)}"
                )

        if item:
            yield from _read(item)
        else:
            with open(self._origin) as file:
                yield from _read(file)


class CSVReader(BaseReader):
    """Reads a CSV file and returns a dictionary per element."""

    def __init__(
        self, *args, mode='r', csv_options=None, as_dict=True, **kwargs
    ):
        """Constructor."""
        self.csv_options = csv_options or {}
        self.as_dict = as_dict
        self.mode = mode
        super().__init__(*args, **kwargs)

    def read(self, item=None):
        """Reads a csv file and returns a dictionary per element."""
        filepath = item or self._origin
        with open(filepath, mode=self.mode) as csvfile:
            if self.as_dict:
                reader = csv.DictReader(csvfile, **self.csv_options)
            else:
                reader = csv.reader(csvfile, **self.csv_options)
            for row in reader:
                yield row
