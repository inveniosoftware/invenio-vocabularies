# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2025 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2024 University of Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabularies configuration."""

import re

from idutils import is_doi, is_gnd, is_isni, is_orcid, is_ror, is_url
from invenio_i18n import lazy_gettext as _

from .datastreams.readers import (
    CSVReader,
    GzipReader,
    JsonLinesReader,
    JsonReader,
    OAIPMHReader,
    RDFReader,
    SimpleHTTPReader,
    SPARQLReader,
    TarReader,
    XMLReader,
    YamlReader,
    ZipReader,
)
from .datastreams.transformers import XMLTransformer
from .datastreams.writers import AsyncWriter, ServiceWriter, YamlWriter
from .resources import VocabulariesResourceConfig
from .services.config import VocabulariesServiceConfig

VOCABULARIES_RESOURCE_CONFIG = VocabulariesResourceConfig
"""Configure the resource."""

VOCABULARIES_SERVICE_CONFIG = VocabulariesServiceConfig
"""Configure the service."""

VOCABULARIES_IDENTIFIER_SCHEMES = {
    "grid": {"label": _("GRID"), "validator": lambda x: True},
    "gnd": {"label": _("GND"), "validator": is_gnd},
    "isni": {"label": _("ISNI"), "validator": is_isni},
    "ror": {"label": _("ROR"), "validator": is_ror},
}
""""Generic identifier schemes, usable by other vocabularies."""

edmo_regexp = re.compile(r"^https://edmo\.seadatanet\.org/report/\d+$")


def is_pic(val):
    """Test if argument is a Participant Identification Code (PIC)."""
    if len(val) != 9:
        return False
    return val.isdigit()


def is_edmo(val):
    """Test if argument is a European Directory of Marine Organisations (EDMO) identifier."""
    return edmo_regexp.match(val)


VOCABULARIES_AFFILIATION_SCHEMES = {
    **VOCABULARIES_IDENTIFIER_SCHEMES,
    "pic": {"label": _("PIC"), "validator": is_pic},
    "edmo": {"label": _("EDMO"), "validator": is_edmo},
}
"""Affiliations allowed identifier schemes."""

VOCABULARIES_FUNDER_SCHEMES = {
    **VOCABULARIES_IDENTIFIER_SCHEMES,
    "doi": {"label": _("DOI"), "validator": is_doi},
}
"""Funders allowed identifier schemes."""

VOCABULARIES_FUNDER_DOI_PREFIX = "10.13039"
"""DOI prefix for the identifier formed with the FundRef id."""

VOCABULARIES_AWARD_SCHEMES = {
    "url": {"label": _("URL"), "validator": is_url},
    "doi": {"label": _("DOI"), "validator": is_doi},
}
"""Awards allowed identifier schemes."""

VOCABULARIES_AWARDS_OPENAIRE_FUNDERS = {
    "aka_________": "05k73zm37",
    "anr_________": "00rbzpz17",
    "arc_________": "05mmh0f86",
    "asap________": "03zj4c476",
    "cihr________": "01gavpb45",
    "corda_______": "00k4n6c32",
    "corda_____he": "00k4n6c32",
    "corda__h2020": "00k4n6c32",
    "euenvagency_": "02k4b9v70",
    "fct_________": "00snfqn58",
    "fwf_________": "013tf3c58",
    "inca________": "03m8vkq32",
    "irb_hr______": "03n51vw80",
    "lcs_________": "02ar66p97",
    "mestd_______": "01znas443",
    "nhmrc_______": "011kf5r70",
    "nih_________": "01cwqze88",
    "nserc_______": "01h531d29",
    "nsf_________": "021nxhr62",
    "nwo_________": "04jsz6e67",
    "rcuk________": "00dq2kk65",  # deprecated funder org
    "sfi_________": "0271asj38",
    "snsf________": "00yjd3n13",
    "sshrc_______": "006cvnv84",
    "tubitakf____": "04w9kkr77",
    "twcf________": "00x0z1472",
    "ukri________": "001aqnf71",
    "wt__________": "029chgv08",
}
"""Mapping of OpenAIRE and ROR funder codes."""

VOCABULARIES_AWARDS_EC_ROR_ID = "00k4n6c32"
"""ROR ID for EC funder."""

VOCABULARIES_NAMES_SCHEMES = {
    "orcid": {"label": _("ORCID"), "validator": is_orcid, "datacite": "ORCID"},
    "isni": {"label": _("ISNI"), "validator": is_isni, "datacite": "ISNI"},
    "gnd": {"label": _("GND"), "validator": is_gnd, "datacite": "GND"},
}
"""Names allowed identifier schemes."""

VOCABULARIES_SUBJECTS_SCHEMES = {
    "gnd": {"label": _("GND"), "validator": is_gnd, "datacite": "GND"},
    "url": {"label": _("URL"), "validator": is_url},
}
"""Subjects allowed identifier schemes."""

VOCABULARIES_CUSTOM_VOCABULARY_TYPES = [
    "names",
    "affiliations",
    "awards",
    "funders",
    "subjects",
]
"""List of custom vocabulary types."""

VOCABULARIES_DATASTREAM_READERS = {
    "csv": CSVReader,
    "json": JsonReader,
    "jsonl": JsonLinesReader,
    "gzip": GzipReader,
    "tar": TarReader,
    "http": SimpleHTTPReader,
    "rdf": RDFReader,
    "sparql": SPARQLReader,
    "yaml": YamlReader,
    "zip": ZipReader,
    "xml": XMLReader,
    "oai-pmh": OAIPMHReader,
}
"""Data Streams readers."""

VOCABULARIES_DATASTREAM_TRANSFORMERS = {
    "xml": XMLTransformer,
}
"""Data Streams transformers."""

VOCABULARIES_DATASTREAM_WRITERS = {
    "service": ServiceWriter,
    "yaml": YamlWriter,
    "async": AsyncWriter,
}
"""Data Streams writers."""

VOCABULARIES_TYPES_SORT_OPTIONS = {
    "name": dict(
        title=_("Name"),
        fields=["id"],
    ),
    "count": dict(
        title=_("Number of entries"),
        fields=["count"],
    ),
}
"""Definitions of available Vocabulary types sort options. """

VOCABULARIES_TYPES_SEARCH = {
    "facets": [],
    "sort": ["name", "count"],
}
"""Vocabulary type search configuration."""

VOCABULARIES_SUBJECTS_EUROSCIVOC_FILE_URL = "https://publications.europa.eu/resource/distribution/euroscivoc/rdf/skos_ap_eu/EuroSciVoc-skos-ap-eu.rdf"
"""Subject EuroSciVoc file download link."""

VOCABULARIES_SUBJECTS_GEMET_FILE_URL = (
    "https://www.eionet.europa.eu/gemet/latest/gemet.rdf.gz"
)
"""Subject GEMET file download link."""

VOCABULARIES_SUBJECTS_NVS_FILE_URL = "http://vocab.nerc.ac.uk/collection/P02/current/?_profile=nvs&_mediatype=application/rdf+xml"
"""Subject NVS-P02 file download link."""

VOCABULARIES_AFFILIATIONS_EDMO_COUNTRY_MAPPING = {
    "Cape Verde": "Cabo Verde",
}
"""Affiliations EDMO Country name remapping dictionary."""

VOCABULARIES_ORCID_ACCESS_KEY = "CHANGEME"
"""ORCID access key to access the s3 bucket."""
VOCABULARIES_ORCID_SECRET_KEY = "CHANGEME"
"""ORCID secret key to access the s3 bucket."""
VOCABULARIES_ORCID_SUMMARIES_BUCKET = "v3.0-summaries"
"""ORCID summaries bucket name."""
VOCABULARIES_ORCID_SYNC_MAX_WORKERS = 32
"""ORCID max number of simultaneous workers/connections."""
VOCABULARIES_ORCID_SYNC_SINCE = {
    "days": 1,
}
"""ORCID time shift to sync. Parameters accepted are the ones passed to 'datetime.timedelta'."""

VOCABULARIES_ORCID_ORG_IDS_MAPPING_PATH = None
"""Path to the CSV file for mapping ORCiD organization IDs to affiliation IDs.

The path can be specified as either an absolute path or a relative path within the
Flask app instance folder (i.e. ``current_app.instance_path``).

The CSV file should have the following columns:

- `org_scheme`: The ORCiD organization ID.
- `org_id`: The ORCiD organization ID.
- `aff_id`: The affiliation ID to map to.
"""
