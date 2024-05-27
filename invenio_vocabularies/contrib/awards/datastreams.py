# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Awards datastreams, transformers, writers and readers."""
import io

import requests
from invenio_access.permissions import system_identity
from invenio_i18n import lazy_gettext as _

from ...datastreams.errors import ReaderError, TransformerError
from ...datastreams.readers import BaseReader
from ...datastreams.transformers import BaseTransformer
from ...datastreams.writers import ServiceWriter
from .config import awards_ec_ror_id, awards_openaire_funders_mapping


class OpenAIREProjectHTTPReader(BaseReader):
    """OpenAIRE Project HTTP Reader returning an in-memory binary stream of the latest OpenAIRE Graph Dataset project tar file."""

    def _iter(self, fp, *args, **kwargs):
        raise NotImplementedError(
            "OpenAIREProjectHTTPReader downloads one file and therefore does not iterate through items"
        )

    def read(self, item=None, *args, **kwargs):
        """Reads the latest OpenAIRE Graph Dataset project tar file from Zenodo and yields an in-memory binary stream of it."""
        if item:
            raise NotImplementedError(
                "OpenAIREProjectHTTPReader does not support being chained after another reader"
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

        # Extract the URL of the only project tar file linked to the record.
        landing_page_project_tar_items = [
            item
            for item in landing_page_linkset["item"]
            if item["type"] == "application/x-tar"
            and item["href"].endswith("/project.tar")
        ]
        if len(landing_page_project_tar_items) != 1:
            raise ReaderError(
                f"Expected 1 project tar item but got {len(landing_page_project_tar_items)}"
            )
        file_url = landing_page_project_tar_items[0]["href"]

        # Download the project tar file and fully load the response bytes content in memory.
        # The bytes content are then wrapped by a BytesIO to be file-like object (as required by `tarfile.open`).
        # Using directly `file_resp.raw` is not possible since `tarfile.open` requires the file-like object to be seekable.
        file_resp = requests.get(file_url)
        file_resp.raise_for_status()
        yield io.BytesIO(file_resp.content)


class AwardsServiceWriter(ServiceWriter):
    """Funders service writer."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        service_or_name = kwargs.pop("service_or_name", "awards")
        super().__init__(service_or_name=service_or_name, *args, **kwargs)

    def _entry_id(self, entry):
        """Get the id from an entry."""
        return entry["id"]


class OpenAIREProjectTransformer(BaseTransformer):
    """Transforms an OpenAIRE project record into an award record."""

    def apply(self, stream_entry, **kwargs):
        """Applies the transformation to the stream entry."""
        record = stream_entry.entry
        award = {}

        code = record["code"]
        openaire_funder_prefix = record["id"].split("::")[0].split("|")[1]
        funder_id = awards_openaire_funders_mapping.get(openaire_funder_prefix)
        if funder_id is None:
            raise TransformerError(
                _(
                    "Unknown OpenAIRE funder prefix {openaire_funder_prefix}".format(
                        openaire_funder_prefix=openaire_funder_prefix
                    )
                )
            )

        award["id"] = f"{funder_id}::{code}"

        funding = next(iter(record.get("funding", [])), None)
        if funding:
            funding_stream_id = funding.get("funding_stream", {}).get("id", "")
            # Example funding stream ID: `EC::HE::HORIZON-AG-UN`. We need the `EC`
            # string, i.e. the second "part" of the identifier.
            program = next(iter(funding_stream_id.split("::")[1:2]), "")
            if program:
                award["program"] = program

        identifiers = []
        if funder_id == awards_ec_ror_id:
            identifiers.append(
                {
                    "identifier": f"https://cordis.europa.eu/projects/{code}",
                    "scheme": "url",
                }
            )
        elif record.get("websiteurl"):
            identifiers.append(
                {"identifier": record.get("websiteurl"), "scheme": "url"}
            )

        if identifiers:
            award["identifiers"] = identifiers

        award["number"] = code
        award["title"] = {"en": record["title"]}
        award["funder"] = {"id": funder_id}
        acronym = record.get("acronym")
        if acronym:
            award["acronym"] = acronym

        stream_entry.entry = award
        return stream_entry


VOCABULARIES_DATASTREAM_READERS = {
    "openaire-project-http": OpenAIREProjectHTTPReader,
}

VOCABULARIES_DATASTREAM_TRANSFORMERS = {
    "openaire-award": OpenAIREProjectTransformer,
}
"""ORCiD Data Streams transformers."""

VOCABULARIES_DATASTREAM_WRITERS = {
    "awards-service": AwardsServiceWriter,
}
"""ORCiD Data Streams transformers."""

DATASTREAM_CONFIG = {
    "readers": [
        {
            "type": "tar",
            "args": {
                "regex": "\\.json.gz$",
                "mode": "r",
            },
        },
        {"type": "gzip"},
        {"type": "jsonl"},
    ],
    "transformers": [
        {"type": "openaire-award"},
    ],
    "writers": [
        {
            "type": "awards-service",
            "args": {
                "identity": system_identity,
            },
        }
    ],
}
"""Data Stream configuration.

An origin is required for the reader.
"""
