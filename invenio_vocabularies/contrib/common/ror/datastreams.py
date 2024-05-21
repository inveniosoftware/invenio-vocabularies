# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""ROR-related Datastreams Readers/Writers/Transformers module."""

import io

import requests

from invenio_vocabularies.datastreams.errors import ReaderError
from invenio_vocabularies.datastreams.readers import BaseReader


class RORHTTPReader(BaseReader):
    """ROR HTTP Reader returning an in-memory binary stream of the latest ROR data dump ZIP file."""

    def _iter(self, fp, *args, **kwargs):
        raise NotImplementedError(
            "RORHTTPReader downloads one file and therefore does not iterate through items"
        )

    def read(self, item=None, *args, **kwargs):
        """Reads the latest ROR data dump ZIP file from Zenodo and yields an in-memory binary stream of it."""
        if item:
            raise NotImplementedError(
                "RORHTTPReader does not support being chained after another reader"
            )

        # Call the signposting `linkset+json` endpoint for the Concept DOI (i.e. latest version) of the ROR data dump.
        # See: https://github.com/inveniosoftware/rfcs/blob/master/rfcs/rdm-0071-signposting.md#provide-an-applicationlinksetjson-endpoint
        headers = {"Accept": "application/linkset+json"}
        api_url = "https://zenodo.org/api/records/6347574"
        api_resp = requests.get(api_url, headers=headers)
        api_resp.raise_for_status()

        # Extract the Landing page Link Set Object located as the first (index 0) item.
        landing_page_linkset = api_resp.json()["linkset"][0]

        # Extract the URL of the only ZIP file linked to the record.
        landing_page_zip_items = [
            item
            for item in landing_page_linkset["item"]
            if item["type"] == "application/zip"
        ]
        if len(landing_page_zip_items) != 1:
            raise ReaderError(
                f"Expected 1 ZIP item but got {len(landing_page_zip_items)}"
            )
        file_url = landing_page_zip_items[0]["href"]

        # Download the ZIP file and fully load the response bytes content in memory.
        # The bytes content are then wrapped by a BytesIO to be file-like object (as required by `zipfile.ZipFile`).
        # Using directly `file_resp.raw` is not possible since `zipfile.ZipFile` requires the file-like object to be seekable.
        file_resp = requests.get(file_url)
        file_resp.raise_for_status()
        yield io.BytesIO(file_resp.content)


VOCABULARIES_DATASTREAM_READERS = {
    "ror-http": RORHTTPReader,
}
