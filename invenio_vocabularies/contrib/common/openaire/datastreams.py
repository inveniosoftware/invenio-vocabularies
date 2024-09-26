# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""OpenAIRE-related Datastreams Readers/Writers/Transformers module."""

import io

import requests

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
            # OpenAIRE Graph Dataset
            api_url = "https://zenodo.org/api/records/3516917"
        elif self._origin == "diff":
            # OpenAIRE Graph dataset: new collected projects
            api_url = "https://zenodo.org/api/records/6419021"
        else:
            raise ReaderError("The --origin option should be either 'full' or 'diff'")

        # Call the signposting `linkset+json` endpoint for the Concept DOI (i.e. latest version) of the OpenAIRE Graph Dataset.
        # See: https://github.com/inveniosoftware/rfcs/blob/master/rfcs/rdm-0071-signposting.md#provide-an-applicationlinksetjson-endpoint
        headers = {"Accept": "application/linkset+json"}
        api_resp = requests.get(api_url, headers=headers)
        api_resp.raise_for_status()

        # Extract the Landing page Link Set Object located as the first (index 0) item.
        landing_page_linkset = api_resp.json()["linkset"][0]

        # Extract the URL of the only tar file matching `tar_href` linked to the record.
        landing_page_matching_tar_items = [
            item
            for item in landing_page_linkset["item"]
            if item["type"] == "application/x-tar"
            and item["href"].endswith(self.tar_href)
        ]
        if len(landing_page_matching_tar_items) != 1:
            raise ReaderError(
                f"Expected 1 tar item matching {self.tar_href} but got {len(landing_page_matching_tar_items)}"
            )
        file_url = landing_page_matching_tar_items[0]["href"]

        # Download the matching tar file and fully load the response bytes content in memory.
        # The bytes content are then wrapped by a BytesIO to be file-like object (as required by `tarfile.open`).
        # Using directly `file_resp.raw` is not possible since `tarfile.open` requires the file-like object to be seekable.
        file_resp = requests.get(file_url)
        file_resp.raise_for_status()
        yield io.BytesIO(file_resp.content)


VOCABULARIES_DATASTREAM_READERS = {
    "openaire-http": OpenAIREHTTPReader,
}

VOCABULARIES_DATASTREAM_TRANSFORMERS = {}

VOCABULARIES_DATASTREAM_WRITERS = {}
