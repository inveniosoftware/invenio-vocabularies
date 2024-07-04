# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
# Copyright (C) 2024 Uni Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabularies admin interface."""
from flask import current_app
from invenio_administration.views.base import AdminResourceListView


class VocabulariesListView(AdminResourceListView):
    """Configuration for vocabularies list view."""

    api_endpoint = "/vocabularies/"
    name = "vocabulary-types"
    menu_label = "Vocabulary Types"
    resource_config = "vocabulary_admin_resource"
    search_request_headers = {"Accept": "application/json"}
    title = "Vocabulary Types"
    category = "Site management"

    pid_path = "id"
    icon = "exchange"
    template = "invenio_administration/search.html"

    display_search = True
    display_delete = False
    display_edit = False
    display_create = False

    item_field_list = {
        "id": {"text": "Name", "order": 1},
        "count": {"text": "Number of entries", "order": 2},
    }

    search_config_name = "VOCABULARIES_TYPES_SEARCH"
    search_facets_config_name = "VOCABULARIES_TYPES_FACETS"
    search_sort_config_name = "VOCABULARIES_TYPES_SORT_OPTIONS"


class VocabularyDetailsListView(AdminResourceListView):
    """Configuration for vocabularies list view."""

    def get_api_endpoint(self, pid_value=None):
        """Overwrite get_api_endpoint to accept pid_value."""
        if pid_value in current_app.config.get(
            "VOCABULARIES_CUSTOM_VOCABULARY_TYPES", []
        ):
            return f"/api/{pid_value}"
        else:
            return f"/api/vocabularies/{pid_value}"

    def get(self, **kwargs):
        """GET view method."""
        parent_context = super().get_context(**kwargs)

        pid_value = kwargs.get("pid_value", "")

        parent_context.update({
            "title": f"{pid_value.capitalize()} vocabulary items",
            "pid_value": pid_value,
        })

        return self.render(**parent_context)

    name = "vocabulary-type-items"
    url = "/vocabulary-types/<pid_value>"

    api_endpoint = "/vocabularies/"

    # INFO name of the resource's list view name, enables navigation between items view and types view.
    list_view_name = "vocabulary-types"

    resource_config = "vocabulary_admin_resource"
    search_request_headers = {"Accept": "application/json"}

    pid_path = "id"

    # INFO only if disabled() (as a function) it's not in the sidebar, see https://github.com/inveniosoftware/invenio-administration/blob/main/invenio_administration/menu/menu.py#L54
    disabled = lambda _: True

    template = "invenio_administration/search.html"

    display_delete = False
    display_create = False
    display_edit = True
    display_search = True

    # TODO: It would be nicer to choose the correct column depending on the vocabulary
    # TODO: It would ne nicer to use the title's translation in the currently selected language and fall back to English if this doesn't exist
    item_field_list = {
        "name": {"text": "Name", "order": 0},
        "title['en']": {"text": "Title [en]", "order": 1},
        "subject": {"text": "Subject", "order": 2},
        "created": {"text": "Created", "order": 3},
    }

    search_config_name = "VOCABULARIES_TYPES_ITEMS_SEARCH"
    search_facets_config_name = "VOCABULARIES_TYPES_ITEMS_FACETS"
    search_sort_config_name = "VOCABULARIES_TYPES_ITEMS_SORT_OPTIONS"
