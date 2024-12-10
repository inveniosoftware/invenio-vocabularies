# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2024 Uni Münster.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabularies admin interface."""

from invenio_administration.views.base import AdminResourceListView
from invenio_i18n import lazy_gettext as _


class VocabulariesListView(AdminResourceListView):
    """Configuration for vocabularies list view."""

    api_endpoint = "/vocabularies/"
    name = "vocabulary-types"
    menu_label = _("Vocabulary Types")
    resource_config = "vocabulary_admin_resource"
    search_request_headers = {"Accept": "application/json"}
    title = _("Vocabulary Types")
    category = _("Site management")

    pid_path = "id"
    icon = "exchange"
    template = "invenio_administration/search.html"

    display_search = True
    display_delete = False
    display_edit = False
    display_create = False

    item_field_list = {
        "id": {"text": _("Name"), "order": 1},
        "count": {"text": _("Number of entries"), "order": 2},
    }

    search_config_name = "VOCABULARIES_TYPES_SEARCH"
    search_facets_config_name = "VOCABULARIES_TYPES_FACETS"
    search_sort_config_name = "VOCABULARIES_TYPES_SORT_OPTIONS"
