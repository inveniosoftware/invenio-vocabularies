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
    AdminResourceDetailView,
    AdminResourceEditView,
    AdminResourceListView,
)
from invenio_i18n import lazy_gettext as _
from flask import current_app


class VocabulariesListView(AdminResourceListView):
    """Configuration for vocabularies list view."""

    api_endpoint = "/vocabularies/"
    name = "Vocabularies"
    resource_config = "vocabulary_admin_resource"
    search_request_headers = {"Accept": "application/json"}
    title = "Vocabulary"
    category = "Site management"

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

    search_config_name = "VOCABULARIES_TYPES_SEARCH"
    search_facets_config_name = "VOCABULARIES_TYPES_FACETS"
    search_sort_config_name = "VOCABULARIES_TYPES_SORT_OPTIONS"

    # resource_name = "vocabulary_admin_resource"


class VocabularyTypesDetailsView(AdminResourceListView):
    """Configuration for vocabularies list view."""

    def get_api_endpoint(self, pid_value=None):
        """overwrite get_api_endpoint to accept pid_value"""

        if pid_value in current_app.config.get("VOCABULARIES_CUSTOM_VOCABULARY_TYPES", []):
            return f"/api/{pid_value}"
        else:
            return f"/api/vocabularies/{pid_value}"

    def get_context(self, **kwargs):
        """Create details view context."""
        search_conf = self.init_search_config(**kwargs)
        schema = self.get_service_schema()
        serialized_schema = self._schema_to_json(schema)
        pid_value = kwargs.get("pid_value", "")
        return {
            "search_config": search_conf,
            "title": f"{pid_value} vocabulary items",
            "name": self.name,
            "resource_schema": serialized_schema,
            "fields": self.item_field_list,
            "display_search": self.display_search,
            "display_create": self.display_create,
            "display_edit": self.display_edit,
            "display_delete": self.display_delete,
            "display_read": self.display_read,
            "actions": self.serialize_actions(),
            "pid_path": self.pid_path,
            "pid_value": pid_value,
            "create_ui_endpoint": self.get_create_view_endpoint(),
            "list_ui_endpoint": self.get_list_view_endpoint(),
            "resource_name": (
                self.resource_name if self.resource_name else self.pid_path
            ),
        }

    name = "Vocabularies_Detail"
    url = "/vocabularies/<pid_value>"

    api_endpoint = "/vocabularies/"

    # INFO name of the resource's list view name, enables navigation between detail view and list view.
    list_view_name = "Vocabularies"

    resource_config = "vocabulary_admin_resource"
    search_request_headers = {"Accept": "application/json"}
    # TODO The title should contain the <pid_value> as well
    # title = f"{pid_value} Detail"
    title = "Vocabularies Detail"
    pid_path = "id"

    # INFO only if disabled() (as a function) its not in the sidebar, see https://github.com/inveniosoftware/invenio-administration/blob/main/invenio_administration/menu/menu.py#L54
    disabled = lambda _: True

    template = "invenio_administration/search.html"

    display_delete = False
    display_create = False
    display_edit = False
    display_search = False

    item_field_list = {
        "id": {"text": "Name", "order": 0},
        "created": {"text": "Created", "order": 1}
    }

    search_config_name = "VOCABULARIES_TYPES_ITEMS_SEARCH"
    search_facets_config_name = "VOCABULARIES_TYPES_ITEMS_FACETS"
    search_sort_config_name = "VOCABULARIES_TYPES_ITEMS_SORT_OPTIONS"

    # search_config_name = "VOCABULARIES_TYPES_SEARCH"
    # search_facets_config_name = "VOCABULARIES_TYPES_FACETS"
    # search_sort_config_name = "VOCABULARIES_TYPES_SORT_OPTIONS"
