# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names datastreams, transformers, writers and readers."""

from invenio_access.permissions import system_identity
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records.dictutils import dict_lookup
from marshmallow import ValidationError

from ...datastreams import StreamEntry
from ...datastreams.errors import TransformerError, WriterError
from ...datastreams.readers import SimpleHTTPReader
from ...datastreams.transformers import BaseTransformer
from ...datastreams.writers import ServiceWriter


class OrcidHTTPReader(SimpleHTTPReader):
    """ORCiD HTTP Reader."""

    def __init__(self, *args, test_mode=True, **kwargs):
        """Constructor."""
        if test_mode:
            origin = "https://sandbox.orcid.org/{id}"
        else:
            origin = "https://orcid.org/{id}"

        super().__init__(origin, *args, **kwargs)


class OrcidTransformer(BaseTransformer):
    """Transforms an ORCiD record into a names record."""

    def apply(self, stream_entry, **kwargs):
        """Applies the transformation to the stream entry."""
        record = stream_entry.entry
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

        stream_entry.entry = entry
        return stream_entry


class NamesServiceWriter(ServiceWriter):
    """Names service writer."""

    def __init__(self, *args, scheme_id="orcid", **kwargs):
        """Constructor."""
        self._scheme_id = scheme_id
        super().__init__(*args, **kwargs)

    def _entry_id(self, entry):
        """Get the id from an entry."""
        for identifier in entry.get("identifiers"):
            if identifier.get("scheme") == self._scheme_id:
                return identifier["identifier"]

    def _resolve(self, id_):
        """Resolve an entry given an id."""
        return self._service.resolve(self._identity, id_=id_, id_type=self._scheme_id)

    def write(self, stream_entry, *args, **kwargs):
        """Writes the input entry using a given service."""
        entry = stream_entry.entry
        try:
            vocab_id = self._entry_id(entry)
            # it is resolved before creation to avoid duplicates since
            # the pid is recidv2 not e.g. the orcid
            current = self._resolve(vocab_id)
            if not self._update:
                raise WriterError([f"Vocabulary entry already exists: {entry}"])
            updated = dict(current.to_dict(), **entry)
            return StreamEntry(
                self._service.update(self._identity, current.id, updated)
            )
        except PIDDoesNotExistError:
            return StreamEntry(self._service.create(self._identity, entry))

        except ValidationError as err:
            raise WriterError([{"ValidationError": err.messages}])


VOCABULARIES_DATASTREAM_READERS = {
    "orcid-http": OrcidHTTPReader,
}


VOCABULARIES_DATASTREAM_TRANSFORMERS = {
    "orcid": OrcidTransformer,
}
"""ORCiD Data Streams transformers."""


VOCABULARIES_DATASTREAM_WRITERS = {
    "names-service": NamesServiceWriter,
}
"""ORCiD Data Streams transformers."""


DATASTREAM_CONFIG = {
    "readers": [
        {
            "type": "tar",
            "args": {
                "regex": ".xml$",
            },
        },
        {"type": "xml"},
    ],
    "transformers": [{"type": "orcid"}],
    "writers": [
        {
            "type": "names-service",
            "args": {
                "service_or_name": "names",
                "identity": system_identity,
            },
        }
    ],
}
"""ORCiD Data Stream configuration.

An origin is required for the reader.
"""
