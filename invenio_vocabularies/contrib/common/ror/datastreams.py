# SPDX-FileCopyrightText: 2024-2026 CERN.
# SPDX-FileCopyrightText: 2024 California Institute of Technology.
# SPDX-License-Identifier: MIT

"""ROR-related Datastreams Readers/Writers/Transformers module."""

import io
from datetime import datetime

from flask import current_app
from idutils import normalize_ror

from invenio_vocabularies.contrib.common.utils import (
    DOIFileFetchError,
    fetch_doi_file,
)
from invenio_vocabularies.datastreams.errors import ReaderError, TransformerError
from invenio_vocabularies.datastreams.readers import BaseReader
from invenio_vocabularies.datastreams.transformers import BaseTransformer

ROR_DATA_DUMP_DOI = "10.5281/zenodo.6347574"


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

    def read(self, item=None, *args, **kwargs):
        """Reads the latest ROR data dump.

        Read from ZIP file from
        Zenodo and yields an in-memory binary stream of it.
        """
        if item:
            raise NotImplementedError(
                "RORHTTPReader does not support being chained after another reader"
            )

        since = (
            datetime.fromisoformat(self._since)
            if self._since and self._since != "None"
            else None
        )
        try:
            content = fetch_doi_file(
                ROR_DATA_DUMP_DOI,
                lambda i: i.get("type") == "application/zip",
                since=since,
            )
        except DOIFileFetchError as e:
            raise ReaderError(str(e)) from e
        if content is None:
            current_app.logger.info(f"Skipping ROR data dump (since: {self._since})")
            return
        yield io.BytesIO(content)


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
