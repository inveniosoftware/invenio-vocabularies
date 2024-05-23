# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2024 Uni Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabularies admin interface."""
from invenio_administration.views.base import (
    AdminResourceListView,
    AdminResourceEditView,
    AdminResourceDetailView,
)
from invenio_i18n import lazy_gettext as _


class VocabulariesListView(AdminResourceListView):
    """Configuration for vocabularies list view."""

    api_endpoint = "/vocabularies/"
    name = "Vocabularies"
    resource_config = "resource"
    search_request_headers = {"Accept": "application/json"}
    title = "Vocabulary"
    category = "Site management"
    # pid_path ist das mapping in welchem JSON key die ID des eintrags steht
    pid_path = "id"
    icon = "exchange"
    template = "invenio_administration/search.html"

    display_search = True
    display_delete = False
    display_edit = False

    item_field_list = {
        "id": {"text": "Name", "order": 1},
        "count": {"text": "Number of entries", "order": 2},
    }

    search_config_name = "VOCABULARIES_SEARCH"
    search_facets_config_name = "VOCABULARIES_FACETS"
    search_sort_config_name = "VOCABULARIES_SORT_OPTIONS"

    resource_name = "vocabulary_admin_resource"


class VocabularyTypesDetailsView(AdminResourceListView):
    """Configuration for vocabularies list view."""

    def get_api_endpoint(self, pid_value=None):
        # overwrite get_api_endpoint to accept pid_value

        return f"/api/vocabularies/{pid_value}"

    name = "Vocabularies_Detail"
    url = "/vocabularies/<pid_value>"
    # FIXME the <pid_value> is not expaned correctly but rather gets passed
    # as an url encoded string like GET /api/vocabularies/%3Cpid_value%3E?q=

    api_endpoint = "/vocabularies/"

    # INFO name of the resource's list view name, enables navigation between detail view and list view.
    list_view_name = "Vocabularies"
    resource_config = "vocabulary_admin_resource"
    search_request_headers = {"Accept": "application/json"}
    # TODO The title should contain the <pid_value> as well
    # title = f"{pid_value} Detail"
    title = "Vocabularies Detail"
    pid_path = "id"
    # pid_value = "id"
    # INFO only if disabled() (as a function) its not in the sidebar, see https://github.com/inveniosoftware/invenio-administration/blob/main/invenio_administration/menu/menu.py#L54
    disabled = lambda _: True

    template = "invenio_administration/search.html"

    display_delete = False
    display_create = False
    display_edit = False
    display_search = False

    item_field_list = {
        "id": {"text": "Name", "order": 0},
        "created": {"text": "Created", "order": 1},
    }
    search_config_name = "VOCABULARIES_SEARCH"
    search_facets_config_name = "VOCABULARIES_FACETS"
    search_sort_config_name = "VOCABULARIES_SORT_OPTIONS"

    # TODO what is this for?
    # "defines a path to human-readable attribute of the resource (title/name etc.)"
    # resource_name = "id"
