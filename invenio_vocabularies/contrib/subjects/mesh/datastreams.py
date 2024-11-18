# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 CERN.
# Copyright (C) 2024 California Institute of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""MeSH subjects datastreams, transformers, writers and readers."""

from invenio_vocabularies.datastreams.transformers import (
    BaseTransformer,
    TransformerError,
)


class MeshSubjectsTransformer(BaseTransformer):
    """MeSH subjects Transformer."""

    def apply(self, stream_entry, *args, **kwargs):
        """Apply transformation on steam entry."""
        entry_data = stream_entry.entry

        # ID in MeSH data is in the URL, ex. https://id.nlm.nih.gov/mesh/D000001
        # We just want to use the ID prefixed by "mesh:""
        try:
            mesh_id = entry_data["id"].split("/")[-1]
            entry_data["id"] = "mesh:" + mesh_id
        except Exception:
            raise TransformerError("Not a valid MeSH ID.")

        entry_data["title"] = title = entry_data.get("title", {})
        # NOTE: MeSH import file comes with an English subject by default
        if "en" not in title:
            title["en"] = entry_data["subject"]

        return stream_entry


VOCABULARIES_DATASTREAM_READERS = {}
"""MeSH datastream readers."""

VOCABULARIES_DATASTREAM_WRITERS = {}
"""MeSH subject datastream writers."""

VOCABULARIES_DATASTREAM_TRANSFORMERS = {"mesh-subjects": MeshSubjectsTransformer}
"""MeSH subjects datastream transformers."""
