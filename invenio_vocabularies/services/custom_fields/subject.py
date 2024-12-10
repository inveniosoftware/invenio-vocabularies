# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.


"""Custom fields."""

from invenio_i18n import lazy_gettext as _

from ...contrib.subjects.api import Subject
from ...contrib.subjects.schema import SubjectRelationSchema
from .vocabulary import VocabularyCF


class SubjectCF(VocabularyCF):
    """Custom field for subjects."""

    field_keys = ["id", "subject"]

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(
            vocabulary_id="subjects",
            schema=SubjectRelationSchema,
            ui_schema=SubjectRelationSchema,
            **kwargs,
        )
        self.pid_field = Subject.pid

    @property
    def mapping(self):
        """Return the mapping."""
        _mapping = {
            "type": "object",
            "properties": {
                "@v": {"type": "keyword"},
                "id": {"type": "keyword"},
                "subject": {"type": "keyword"},
            },
        }

        return _mapping


SUBJECT_FIELDS_UI = [
    {
        "section": _("Subjects"),
        "fields": [
            dict(
                field="subjects",
                ui_widget="SubjectAutocompleteDropdown",
                isGenericVocabulary=False,
                props=dict(
                    label=_("Keywords and subjects"),
                    icon="tag",
                    description=_("The subjects related to the community"),
                    placeholder=_("Search for a subject by name e.g. Psychology ..."),
                    autocompleteFrom="api/subjects",
                    noQueryMessage=_("Search for subjects..."),
                    autocompleteFromAcceptHeader="application/vnd.inveniordm.v1+json",
                    required=False,
                    multiple=True,
                    clearable=True,
                    allowAdditions=False,
                ),
                template="invenio_vocabularies/subjects.html",
            )
        ],
    }
]


SUBJECT_FIELDS = {
    SubjectCF(
        name="subjects",
        multiple=True,
        dump_options=False,
    )
}
