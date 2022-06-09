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

from .datastreams.readers import (
    CSVReader,
    GzipReader,
    JsonLinesReader,
    JsonReader,
    TarReader,
    XMLReader,
    YamlReader,
    ZipReader,
)
from .datastreams.transformers import XMLTransformer
from .datastreams.writers import ServiceWriter, YamlWriter
from .resources.resource import VocabulariesResourceConfig
from .services.service import VocabulariesServiceConfig

VOCABULARIES_RESOURCE_CONFIG = VocabulariesResourceConfig
"""Configure the resource."""

VOCABULARIES_SERVICE_CONFIG = VocabulariesServiceConfig
"""Configure the service."""

VOCABULARIES_IDENTIFIER_SCHEMES = {
    "grid": {"label": _("GRID"), "validator": lambda x: True},
    "gnd": {"label": _("GND"), "validator": idutils.is_gnd},
    "isni": {"label": _("ISNI"), "validator": idutils.is_isni},
    "ror": {"label": _("ROR"), "validator": idutils.is_ror},
}
""""Generic identifier schemes, usable by other vocabularies."""

VOCABULARIES_AFFILIATION_SCHEMES = {
    **VOCABULARIES_IDENTIFIER_SCHEMES,
}
"""Affiliations allowed identifier schemes."""

VOCABULARIES_FUNDER_SCHEMES = {
    **VOCABULARIES_IDENTIFIER_SCHEMES,
    "doi": {"label": _("DOI"), "validator": idutils.is_doi},
}
"""Funders allowed identifier schemes."""

VOCABULARIES_FUNDER_DOI_PREFIX = "10.13039"
"""DOI prefix for the identifier formed with the FundRef id."""

VOCABULARIES_AWARD_SCHEMES = {
    "url": {"label": _("URL"), "validator": idutils.is_url},
    "doi": {"label": _("DOI"), "validator": idutils.is_doi},
}
"""Awards allowed identifier schemes."""

VOCABULARIES_AWARDS_OPENAIRE_FUNDERS = {
    "anr_________": "00rbzpz17",
    "aka_________": "05k73zm37",
    "arc_________": "05mmh0f86",
    "cihr________": "01gavpb45",
    "corda_______": "00k4n6c32",
    "corda__h2020": "00k4n6c32",
    "euenvagency_": "02k4b9v70",
    "fct_________": "00snfqn58",
    "fwf_________": "013tf3c58",
    "irb_hr______": "03n51vw80",
    "mestd_______": "01znas443",
    "nhmrc_______": "011kf5r70",
    "nih_________": "01cwqze88",
    "nserc_______": "01h531d29",
    "nsf_________": "021nxhr62",
    "nwo_________": "04jsz6e67",
    "rcuk________": "10.13039/501100000690",
    "ukri________": "001aqnf71",
    "sfi_________": "0271asj38",
    "snsf________": "00yjd3n13",
    "sshrc_______": "006cvnv84",
    "tubitakf____": "04w9kkr77",
    "wt__________": "029chgv08",
}
"""Mapping of OpenAIRE and ROR funder codes."""

VOCABULARIES_AWARDS_EC_ROR_ID = "00k4n6c32"
"""ROR ID for EC funder."""

VOCABULARIES_NAMES_SCHEMES = {
    "orcid": {"label": _("ORCID"), "validator": idutils.is_orcid, "datacite": "ORCID"},
    "isni": {"label": _("ISNI"), "validator": idutils.is_isni, "datacite": "ISNI"},
    "gnd": {"label": _("GND"), "validator": idutils.is_gnd, "datacite": "GND"},
}
"""Names allowed identifier schemes."""

VOCABULARIES_DATASTREAM_READERS = {
    "csv": CSVReader,
    "json": JsonReader,
    "jsonl": JsonLinesReader,
    "gzip": GzipReader,
    "tar": TarReader,
    "yaml": YamlReader,
    "zip": ZipReader,
    "xml": XMLReader,
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
