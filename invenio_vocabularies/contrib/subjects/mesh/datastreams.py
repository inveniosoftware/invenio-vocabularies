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

        # ID in MeSH data is the URL, ex. https://id.nlm.nih.gov/mesh/D000001
        # We just want to use the ID prefixed by "mesh:""
        try:
            mesh_id = entry_data["id"].split("/")[-1]
        except Exception:
            raise TransformerError("Not a valid MeSH ID.")

        entry_data["id"] = "mesh:" + mesh_id
        return stream_entry


VOCABULARIES_DATASTREAM_READERS = {}
"""MeSH datastream readers."""

VOCABULARIES_DATASTREAM_WRITERS = {}
"""MeSH subject datastream writers."""

VOCABULARIES_DATASTREAM_TRANSFORMERS = {"mesh-subjects": MeshSubjectsTransformer}
"""MeSH subjects datastream transformers."""
