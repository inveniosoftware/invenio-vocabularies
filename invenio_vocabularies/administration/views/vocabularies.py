from functools import partial

from flask import current_app
from invenio_administration.views.base import (
    AdminResourceDetailView,
    AdminResourceListView,
)
from invenio_i18n import lazy_gettext as _
from invenio_search_ui.searchconfig import search_app_config


class VocabulariesListView(AdminResourceListView):
    """Configuration for OAI-PMH sets list view."""

    api_endpoint = "/vocabularies/"
    name = "Vocabularies"
    resource_config = "resource"
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

    search_config_name = "VOCABULARIES_SEARCH"
    search_facets_config_name = "VOCABULARIES_FACETS"
    search_sort_config_name = "VOCABULARIES_SORT_OPTIONS"

    resource_name = "resource"
