# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 California Institute of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""ROR-related Datastreams Readers/Writers/Transformers module."""

import io

import requests
from idutils import normalize_ror

from invenio_vocabularies.datastreams.errors import ReaderError, TransformerError
from invenio_vocabularies.datastreams.readers import BaseReader
from invenio_vocabularies.datastreams.transformers import BaseTransformer

from .config import funder_fundref_doi_prefix, funder_schemes


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


class RORTransformer(BaseTransformer):
    """Transforms a JSON ROR record into a funders record."""

    def apply(self, stream_entry, **kwargs):
        """Applies the transformation to the stream entry."""
        record = stream_entry.entry
        funder = {}
        funder["title"] = {}

        funder["id"] = normalize_ror(record.get("id"))
        if not funder["id"]:
            raise TransformerError(_("Id not found in ROR entry."))

        aliases = []
        acronym = None
        for name in record.get("names"):
            lang = name.get("lang", "en")
            if "ror_display" in name["types"]:
                funder["name"] = name["value"]
            if "label" in name["types"]:
                funder["title"][lang] = name["value"]
            if "alias" in name["types"]:
                aliases.append(name["value"])
            if "acronym" in name["types"]:
                # The first acronyn goes in acronym field to maintain
                # compatability with existing data structure
                if not acronym:
                    acronym = name["value"]
                else:
                    aliases.append(name["value"])
        if acronym:
            funder["acronym"] = acronym
        if aliases:
            funder["aliases"] = aliases

        # ror_display is required and should be in every entry
        if not funder["name"]:
            raise TransformerError(
                _("Name with type ror_display not found in ROR entry.")
            )

        # This only gets the first location, to maintain compatability
        # with existing data structure
        location = record.get("locations", [{}])[0].get("geonames_details", {})
        funder["country"] = location.get("country_code")
        funder["country_name"] = location.get("country_name")
        funder["location_name"] = location.get("name")

        funder["types"] = record.get("types")

        status = record.get("status")
        funder["status"] = status

        # The ROR is always listed in identifiers, expected by serialization
        funder["identifiers"] = [{"identifier": funder["id"], "scheme": "ror"}]
        valid_schemes = set(funder_schemes.keys())
        fund_ref = "fundref"
        valid_schemes.add(fund_ref)
        for identifier in record.get("external_ids"):
            scheme = identifier["type"]
            if scheme in valid_schemes:
                value = identifier.get("preferred") or identifier.get("all")[0]
                if scheme == fund_ref:
                    value = f"{funder_fundref_doi_prefix}/{value}"
                    scheme = "doi"
                funder["identifiers"].append(
                    {
                        "identifier": value,
                        "scheme": scheme,
                    }
                )

        stream_entry.entry = funder
        return stream_entry


VOCABULARIES_DATASTREAM_TRANSFORMERS = {
    "ror-funder": RORTransformer,
}
