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

    name = "Vocabularies_Detail"
    url = "/vocabularies/<pid_value>"
    # FIXME the <pid_value> is not expaned correctly but rather gets passed as an url encoded string like GET /api/vocabularies/%3Cpid_value%3E?q=
    api_endpoint = "/vocabularies/<pid_value>"

    # name of the resource's list view name, enables navigation between detail view and list view.
    list_view_name = "Vocabularies"
    resource_config = "vocabulary_admin_resource"
    search_request_headers = {"Accept": "application/json"}
    title = "Vocabularies Detail"
    pid_path = "id"
    pid_value = "id"
    # only if disabled() (as a function) its not in the sidebar, see https://github.com/inveniosoftware/invenio-administration/blob/main/invenio_administration/menu/menu.py#L54
    disabled = lambda _: True

    list_view_name = "Vocabularies"
    template = "invenio_administration/search.html"
    display_delete = False
    display_create = False
    display_edit = False
    display_search = True
    item_field_list = {
        "id": {"text": "Name", "order": 1},
    }
    search_config_name = "VOCABULARIES_SEARCH"
    search_facets_config_name = "VOCABULARIES_FACETS"
    search_sort_config_name = "VOCABULARIES_SORT_OPTIONS"
    resource_name = "resource"
