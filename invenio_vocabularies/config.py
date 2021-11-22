# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabularies configuration."""

import idutils
from flask_babelex import lazy_gettext as _

from .datastreams.readers import TarReader, YamlReader
from .datastreams.transformers import XMLTransformer
from .datastreams.writers import ServiceWriter, YamlWriter
from .resources.resource import VocabulariesResourceConfig
from .services.service import VocabulariesServiceConfig

VOCABULARIES_RESOURCE_CONFIG = VocabulariesResourceConfig
"""Configure the resource."""

VOCABULARIES_SERVICE_CONFIG = VocabulariesServiceConfig
"""Configure the service."""

VOCABULARIES_AFFILIATION_SCHEMES = {
    "grid": {
        "label": _("GRID"),
        "validator": lambda x: True
    },
    "gnd": {
        "label": _("GND"),
        "validator": idutils.is_gnd
    },
    "isni": {
        "label": _("ISNI"),
        "validator": idutils.is_isni
    },
    "ror": {
        "label": _("ROR"),
        "validator": idutils.is_ror
    },
}
"""Affiliations allowed identifier schemes."""

VOCABULARIES_NAMES_SCHEMES = {
    "orcid": {
        "label": _("ORCID"),
        "validator": idutils.is_orcid,
        "datacite": "ORCID"
    },
    "gnd": {
        "label": _("GND"),
        "validator": idutils.is_gnd,
        "datacite": "GND"
    }
}
"""Names allowed identifier schemes."""

VOCABULARIES_DATASTREAM_READERS = {
    "tar": TarReader,
    "yaml": YamlReader,
}
"""Data Streams readers."""

VOCABULARIES_DATASTREAM_TRANSFORMERS = {
    "xml": XMLTransformer,
}
"""Data Streams transformers."""

VOCABULARIES_DATASTREAM_WRITERS = {
    "service": ServiceWriter,
    "yaml": YamlWriter,
}
"""Data Streams writers."""
