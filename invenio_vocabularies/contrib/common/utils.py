# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Utility functions for Invenio-Vocabularies HTTP operations."""

from datetime import datetime

import requests
from flask import current_app, has_app_context


class DOIFileFetchError(Exception):
    """Raised when a file cannot be fetched from a DOI via signposting."""


def invenio_user_agent(default="Invenio"):
    """Return a User-Agent string, using Flask config if available."""
    if has_app_context():
        hostname = current_app.config.get("SITE_HOSTNAME", default)
        ui_url = current_app.config.get("SITE_UI_URL", None)
        return f"{hostname} (+{ui_url})" if ui_url else hostname
    return default


def fetch_doi_file(doi, select_func, since=None):
    """Fetch one file linked from a DOI via FAIR signposting.

    Resolves the linksets advertised at ``doi`` (signposting profile,
    RFC 9264 / inveniosoftware RDM-0071), picks the single item whose
    metadata matches ``select_func``, and returns the bytes at its
    ``href``. When ``since`` is given, the record's publication date
    is read from the JSON-LD ``describedby`` entry first; if the
    record was not republished after ``since``, ``None`` is returned
    without fetching the file.

    See https://github.com/inveniosoftware/rfcs/blob/master/rfcs/rdm-0071-signposting.md

    :param doi: DOI (e.g. ``10.5281/zenodo.6347574``).
    :param select_func: Callable invoked with each linkset ``item`` dict; the single
        item for which it returns truthy is fetched.
    :param since: Optional ``datetime``. The file is fetched only when the record was
        republished at or after this point.
    """
    if not doi.startswith(("http://", "https://")):
        doi = f"https://doi.org/{doi}"

    with requests.Session() as session:
        session.headers["User-Agent"] = invenio_user_agent()

        # Resolve the DOI to the linkset endpoint via the rel="linkset" Link header.
        resp = session.get(doi, allow_redirects=True)
        resp.raise_for_status()
        if "linkset" not in resp.links:
            raise DOIFileFetchError(f"Linkset not found at {doi}")
        linkset_resp = session.get(
            resp.links["linkset"]["url"],
            headers={"Accept": "application/linkset+json"},
        )
        linkset_resp.raise_for_status()
        linksets = linkset_resp.json()["linkset"]

        # If `since` is set, skip when the record's publication date is older.
        if since is not None:
            ld_link = next(
                (
                    fmt
                    for linkset in linksets
                    for fmt in linkset.get("describedby", [])
                    if fmt.get("type") == "application/ld+json"
                ),
                None,
            )
            if ld_link is None:
                raise DOIFileFetchError(f"No JSON-LD describedby entry found for {doi}")
            ld_resp = session.get(ld_link["href"], headers={"Accept": ld_link["type"]})
            ld_resp.raise_for_status()
            ld_data = ld_resp.json()
            date_str = ld_data.get("dateCreated") or ld_data.get("datePublished")
            if not date_str:
                raise DOIFileFetchError(
                    f"JSON-LD at {ld_link['href']} has no dateCreated or datePublished"
                )
            pub_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            if pub_date < since:
                return None

        # Pick the single matching item and download it.
        matches = [
            item
            for linkset in linksets
            for item in linkset.get("item", [])
            if select_func(item)
        ]
        if len(matches) != 1:
            raise DOIFileFetchError(
                f"Expected 1 matching linkset item at {doi}, got {len(matches)}"
            )
        file_resp = session.get(matches[0]["href"])
        file_resp.raise_for_status()
        return file_resp.content
