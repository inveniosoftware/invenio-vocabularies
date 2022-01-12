# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names datastreams, transformers, writers and readers."""

from invenio_access.permissions import system_identity
from invenio_records.dictutils import dict_lookup

from ...datastreams import StreamEntry
from ...datastreams.errors import TransformerError
from ...datastreams.transformers import XMLTransformer


class OrcidXMLTransformer(XMLTransformer):
    """ORCiD XML Transfomer."""

    def apply(self, stream_entry, **kwargs):
        """Applies the transformation to the stream entry."""
        xml_tree = self._xml_to_etree(stream_entry.entry)
        researcher = self._etree_to_dict(xml_tree)
        record = researcher["html"]["body"].get("record")

        if not record:
            raise TransformerError(f"Record not found in ORCiD entry.")

        person = record["person"]
        orcid_id = record["orcid-identifier"]["uri"]

        name = person.get("name")
        if name is None:
            raise TransformerError(f"Name not found in ORCiD entry.")

        entry = {
            "given_name": name.get("given-names"),
            "family_name": name.get("family-name"),
            "identifiers": [{"scheme": "orcid", "identifier": orcid_id}],
            "affiliations": [],
        }

        try:
            employments = dict_lookup(
                record, "activities-summary.employments.affiliation-group"
            )
            if isinstance(employments, dict):
                employments = [employments]
            history = set()
            for employment in employments:
                terminated = employment["employment-summary"].get("end-date")
                affiliation = dict_lookup(
                    employment,
                    "employment-summary.organization.name",
                )
                if affiliation not in history and not terminated:
                    history.add(affiliation)
                    entry["affiliations"].append({"name": affiliation})
        except Exception:
            pass

        return StreamEntry(entry)


VOCABULARIES_DATASTREAM_TRANSFORMERS = {
    "orcid-xml": OrcidXMLTransformer,
}
"""ORCiD Data Streams transformers."""

DATASTREAM_CONFIG = {
    "reader": {
        "type": "tar",
        "args": {
            "regex": ".xml$",
        }
    },
    "transformers": [
        {"type": "orcid-xml"}
    ],
    "writers": [{
        "type": "service",
        "args": {
            "service_or_name": "rdm-names",
            "identity": system_identity,
        }
    }],
}
"""ORCiD Data Stream configuration.

An origin is required for the reader.
"""
