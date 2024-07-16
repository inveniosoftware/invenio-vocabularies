# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2024 Uni Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabularies admin interface."""
from flask import current_app
from functools import partial
from invenio_search_ui.searchconfig import search_app_config, SortConfig, FacetsConfig
from invenio_administration.views.base import (
    AdminResourceEditView,
    AdminResourceListView,
)


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

    def init_search_config(self, **kwargs):
        """Build search view config."""
        pid_value = kwargs.get("pid_value", "")
        custom_search_config = current_app.config[self.search_config_name].get(pid_value)

        if custom_search_config:
            available_sort_options = current_app.config[self.search_sort_config_name]
            available_facets = current_app.config.get(self.search_facets_config_name)

            return partial(
                search_app_config,
                config_name=self.get_search_app_name(**kwargs),
                available_facets=available_facets,
                sort_options=available_sort_options,
                endpoint=self.get_api_endpoint(**kwargs),
                headers=self.get_search_request_headers(**kwargs),
                sort=SortConfig(available_sort_options,
                                custom_search_config["sort"],
                                custom_search_config["sort_default"],
                                custom_search_config["sort_default_no_query"]),
                facets=FacetsConfig(available_facets, custom_search_config["facets"]),
            )
        else:
            return super().init_search_config(**kwargs)

    def get(self, **kwargs):
        """GET view method."""
        parent_context = super().get_context(**kwargs)

        pid_value = kwargs.get("pid_value", "")
        vocab_admin_cfg = current_app.config["VOCABULARIES_ADMINISTRATION_CONFIG"]

        custom_config = vocab_admin_cfg.get(pid_value)

        if custom_config:
            parent_context.update(custom_config)
        else:
            parent_context.update({
                "title": f"{pid_value.capitalize()} vocabulary items"
            })

        return self.render(**parent_context)

    name = "vocabulary-type-items"
    url = "/vocabulary-types/<pid_value>"

    # INFO name of the resource's list view name, enables navigation between items view and types view.
    list_view_name = "vocabulary-types"

    resource_config = "vocabulary_admin_resource"
    search_request_headers = {"Accept": "application/json"}

    pid_path = "id"
    resource_name = "title['en']"

    # INFO only if disabled() (as a function) it's not in the sidebar, see https://github.com/inveniosoftware/invenio-administration/blob/main/invenio_administration/menu/menu.py#L54
    disabled = lambda _: True

    template = "invenio_administration/search.html"

    display_delete = False
    display_create = False
    display_edit = True
    display_search = True

    # TODO: It would ne nicer to use the title's translation in the currently selected language and fall back to English if this doesn't exist
    item_field_list = {
        "title['en']": {"text": "Title [en]", "order": 0},
        "created": {"text": "Created", "order": 1},
    }

    search_config_name = "VOCABULARIES_TYPES_ITEMS_SEARCH"
    search_facets_config_name = "VOCABULARIES_TYPES_ITEMS_FACETS"
    search_sort_config_name = "VOCABULARIES_TYPES_ITEMS_SORT_OPTIONS"
