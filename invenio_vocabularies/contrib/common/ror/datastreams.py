# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 CERN.
# Copyright (C) 2024 California Institute of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""ROR-related Datastreams Readers/Writers/Transformers module."""

import io

import arrow
import requests
from flask import current_app
from idutils import normalize_ror

from invenio_vocabularies.datastreams.errors import ReaderError, TransformerError
from invenio_vocabularies.datastreams.readers import BaseReader
from invenio_vocabularies.datastreams.transformers import BaseTransformer


class RORHTTPReader(BaseReader):
    """ROR HTTP Reader.

    Returning an in-memory
    binary stream of the latest ROR data dump ZIP file.
    """

    def __init__(self, origin=None, mode="r", since=None, *args, **kwargs):
        """Constructor."""
        self._since = since
        super().__init__(origin, mode, *args, **kwargs)

    def _iter(self, fp, *args, **kwargs):
        raise NotImplementedError(
            "RORHTTPReader downloads one file "
            "and therefore does not iterate through items"
        )

    def _get_last_dump_date(self, linksets):
        """Get the last dump date."""
        for linkset in linksets:
            metadata_formats = linkset.get("describedby", [])
            for format_link in metadata_formats:
                if format_link.get("type") == "application/ld+json":
                    json_ld_reponse = requests.get(
                        format_link["href"],
                        headers={"Accept": format_link["type"]},
                    )
                    json_ld_reponse.raise_for_status()
                    json_ld_data = json_ld_reponse.json()

                    last_dump_date = arrow.get(
                        json_ld_data.get("dateCreated")
                        or json_ld_data.get("datePublished")
                    )
                    return last_dump_date
        else:
            raise ReaderError(
                "Couldn't find JSON-LD in publisher's linkset "
                "to determine last dump date."
            )

    def read(self, item=None, *args, **kwargs):
        """Reads the latest ROR data dump.

        Read from ZIP file from
        Zenodo and yields an in-memory binary stream of it.
        """
        if item:
            raise NotImplementedError(
                "RORHTTPReader does not support being chained after another reader"
            )

        # Follow the DOI to get the link of the linkset
        dataset_doi_link = "https://doi.org/10.5281/zenodo.6347574"
        landing_page = requests.get(dataset_doi_link, allow_redirects=True)
        landing_page.raise_for_status()

        # Call the signposting `linkset+json` endpoint for
        # the Concept DOI (i.e. latest version) of the ROR data dump.
        # See: https://github.com/inveniosoftware/rfcs/blob/master/rfcs/rdm-0071-signposting.md#provide-an-applicationlinksetjson-endpoint
        if "linkset" not in landing_page.links:
            raise ReaderError("Linkset not found in the ROR dataset record.")
        linkset_response = requests.get(
            landing_page.links["linkset"]["url"],
            headers={"Accept": "application/linkset+json"},
        )
        linkset_response.raise_for_status()
        linksets = linkset_response.json()["linkset"]

        if self._since:
            last_dump_date = self._get_last_dump_date(linksets)
            if last_dump_date < arrow.get(self._since):
                current_app.logger.info(
                    f"Skipping ROR data dump (last dump: {last_dump_date}, since: {self._since})"
                )
                return

        for linkset in linksets:
            items = linkset.get("item", [])
            zip_files = [item for item in items if item["type"] == "application/zip"]
            if len(zip_files) == 1:
                file_url = zip_files[0]["href"]
                break
            if len(zip_files) > 1:
                raise ReaderError(f"Expected 1 ZIP item but got {len(zip_files)}")

        current_app.logger.info(f"Reading ROR data dump (URL: {file_url})")

        # Download the ZIP file and fully load the response bytes content in memory.
        # The bytes content are then wrapped by a BytesIO to be
        # file-like object (as required by `zipfile.ZipFile`).
        # Using directly `file_resp.raw` is not possible since
        # `zipfile.ZipFile` requires the file-like object to be seekable.
        file_resp = requests.get(file_url)
        file_resp.raise_for_status()
        yield io.BytesIO(file_resp.content)


VOCABULARIES_DATASTREAM_READERS = {
    "ror-http": RORHTTPReader,
}


class RORTransformer(BaseTransformer):
    """Transforms a JSON ROR record into a funders record."""

    def __init__(
        self, *args, vocab_schemes=None, funder_fundref_doi_prefix=None, **kwargs
    ):
        """Initializes the transformer."""
        self.vocab_schemes = vocab_schemes
        self.funder_fundref_doi_prefix = funder_fundref_doi_prefix
        super().__init__(*args, **kwargs)

    def apply(self, stream_entry, **kwargs):
        """Applies the transformation to the stream entry."""
        record = stream_entry.entry
        ror = {}
        ror["title"] = {}

        ror["id"] = normalize_ror(record.get("id"))
        if not ror["id"]:
            raise TransformerError(_("Id not found in ROR entry."))

        # Using set so aliases are unique
        aliases = set()
        acronym = None
        for name in record.get("names"):
            lang = name.get("lang", "en")
            if lang == None:
                lang = "en"
            if "ror_display" in name["types"]:
                ror["name"] = name["value"]
            if "label" in name["types"]:
                ror["title"][lang] = name["value"]
            if "alias" in name["types"]:
                aliases.add(name["value"])
            if "acronym" in name["types"]:
                # The first acronyn goes in acronym field to maintain
                # compatability with existing data structure
                if not acronym:
                    acronym = name["value"]
                else:
                    aliases.add(name["value"])
        if "en" not in ror["title"]:
            ror["title"]["en"] = ror["name"]
        if acronym:
            ror["acronym"] = acronym
        if aliases:
            ror["aliases"] = list(aliases)

        # ror_display is required and should be in every entry
        if not ror["name"]:
            raise TransformerError(
                _("Name with type ror_display not found in ROR entry.")
            )

        # This only gets the first location, to maintain compatability
        # with existing data structure
        location = record.get("locations", [{}])[0].get("geonames_details", {})
        ror["country"] = location.get("country_code")
        ror["country_name"] = location.get("country_name")
        ror["location_name"] = location.get("name")

        ror["types"] = record.get("types")

        status = record.get("status")
        ror["status"] = status

        # The ROR is always listed in identifiers, expected by serialization
        ror["identifiers"] = [{"identifier": ror["id"], "scheme": "ror"}]
        if self.vocab_schemes:
            valid_schemes = set(self.vocab_schemes.keys())
        else:
            valid_schemes = set()
        fund_ref = "fundref"
        if self.funder_fundref_doi_prefix:
            valid_schemes.add(fund_ref)
        for identifier in record.get("external_ids"):
            scheme = identifier["type"]
            if scheme in valid_schemes:
                value = identifier.get("preferred") or identifier.get("all")[0]
                if scheme == fund_ref:
                    if self.funder_fundref_doi_prefix:
                        value = f"{self.funder_fundref_doi_prefix}/{value}"
                        scheme = "doi"
                ror["identifiers"].append(
                    {
                        "identifier": value,
                        "scheme": scheme,
                    }
                )

        stream_entry.entry = ror
        return stream_entry


VOCABULARIES_DATASTREAM_TRANSFORMERS = {
    "ror": RORTransformer,
}

VOCABULARIES_DATASTREAM_WRITERS = {}
