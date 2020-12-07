# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary API."""

from babel import Locale, default_locale
from flask_babelex import lazy_gettext as _

from invenio_vocabularies.records.api import Vocabulary


class VocabularyItem(dict):
    """A wrapper for a single vocabulary item."""

    def _get_l10n(self, prop, locale):
        """Collapses an internationalized field into a localized one."""
        messages = self.get("metadata", {}).get(prop, {})
        return messages.get(locale) or messages.get(
            Locale.parse(default_locale()).language
        )

    def get_description(self, locale):
        """Localized description."""
        return self._get_l10n("description", locale)

    def get_title(self, locale):
        """Localized title."""
        return self._get_l10n("title", locale)

    def dump(self, locale):
        """Returns a localized copy of this object."""
        return {
            **self,
            "description": self.get_description(locale),
            "title": self.get_title(locale),
        }


class VocabularyBackend:
    """A backend implementation for a vocabulary type."""

    record_cls = Vocabulary

    def get(self, identifier):
        """Returns the vocabulary item matching this identifier."""
        return VocabularyItem(self.record_cls.pid.resolve(identifier))

    def get_all(self, vocabulary_type_name):
        """Returns all the vocabulary of this type. Potentially costly."""
        # TODO implement
        pass


class ResourceTypeVocabulary:
    """An API for a vocabulary type."""

    title = _("Resource Type")
    backend = VocabularyBackend()

    def __init__(self, vocabulary_type):
        """Constructs a new vocabulary type."""
        super().__init__()
        self.vocabulary_type = vocabulary_type

    def get(self, identifier):
        """Returns the vocabulary item matching this identifier."""
        return self.backend.get(identifier)

    def get_all(self):
        """Returns all the vocabulary of this type."""
        return self.backend.get_all(self.vocabulary_type)

    def dump_all(self):
        """Dumps all the vocabulary of this type."""
        return list(map(lambda v: v.dump(), self.get_all()))


class VocabularyRegistry:
    """A registry of all the vocabulary type."""

    @staticmethod
    def get(vocabulary_type):
        """Get an instance of a vocabulary type."""
        return ResourceTypeVocabulary(vocabulary_type)
