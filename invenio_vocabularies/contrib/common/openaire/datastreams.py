# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""OpenAIRE-related Datastreams Readers/Writers/Transformers module."""

import io

from invenio_vocabularies.contrib.common.utils import (
    DOIFileFetchError,
    fetch_doi_file,
)
from invenio_vocabularies.datastreams.errors import ReaderError
from invenio_vocabularies.datastreams.readers import BaseReader


class OpenAIREHTTPReader(BaseReader):
    """OpenAIRE HTTP Reader returning an in-memory binary stream of the latest OpenAIRE Graph Dataset tar file of a given type."""

    def __init__(self, origin=None, mode="r", tar_href=None, *args, **kwargs):
        """Constructor."""
        self.tar_href = tar_href
        super().__init__(origin, mode, *args, **kwargs)

    def _iter(self, fp, *args, **kwargs):
        raise NotImplementedError(
            "OpenAIREHTTPReader downloads one file and therefore does not iterate through items"
        )

    def read(self, item=None, *args, **kwargs):
        """Reads the latest OpenAIRE Graph Dataset tar file of a given type from Zenodo and yields an in-memory binary stream of it."""
        if item:
            raise NotImplementedError(
                "OpenAIREHTTPReader does not support being chained after another reader"
            )

        if self._origin == "full":
            # OpenAIRE Graph Dataset (concept DOI)
            doi = "10.5281/zenodo.3516917"
        elif self._origin == "diff":
            # OpenAIRE Graph Dataset: new collected projects (concept DOI)
            doi = "10.5281/zenodo.6419021"
        else:
            raise ReaderError("The --origin option should be either 'full' or 'diff'")

        try:
            file_bytes = fetch_doi_file(
                doi,
                lambda item: item.get("type") == "application/x-tar"
                and item.get("href", "").endswith(self.tar_href),
            )
        except DOIFileFetchError as e:
            raise ReaderError(str(e)) from e
        yield io.BytesIO(file_bytes)


VOCABULARIES_DATASTREAM_READERS = {
    "openaire-http": OpenAIREHTTPReader,
}

VOCABULARIES_DATASTREAM_TRANSFORMERS = {}

VOCABULARIES_DATASTREAM_WRITERS = {}
