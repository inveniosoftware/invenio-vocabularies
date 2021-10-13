# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Prioritized importer."""

from collections import defaultdict
from pathlib import Path

import pkg_resources
from sqlalchemy.orm import load_only

from ..records.models import VocabularyScheme, VocabularyType
from .errors import ConflictingOriginError
from .local import LocalImporter


class PrioritizedImporter:
    """Concept of Vocabulary fixtures across locations.

    This class' responsibility is to load different vocabularies in
    this priority order: app_data, then extensions and then this package.

    Earlier vocabularies in this hierarchy are chosen first. But in the case
    of subvocabularies (e.g. subject types), having loaded a subvocabulary
    before, shouldn't prevent loading another one. Only if the same
    subvocabulary is encountered again should it be ignored.

    Concretely, having loaded MeSH subjects shouldn't prevent loading FAST
    subjects even though they are both under the "subjects" vocabulary.
    Another MeSH subject encountered down the hierarchy is ignored however.
    """

    def __init__(self, identity, app_data_folder=None, pkg_data_folder=None,
                 filename="vocabularies.yaml", delay=True):
        """Constructor.

        identity: Identity to use when loading
        app_data_folder: Path object to instance data folder
        pkg_data_folder: Path object to this package's data folder.
                         Defaults to `./data` and really only changeable for
                         tests.
        filename: vocabularies filename to check at each location
        """
        self._identity = identity
        # Path("./app_data") assumes app_data is in current working directory
        self._app_data_folder = app_data_folder or Path("./app_data")
        self._pkg_data_folder = (
            pkg_data_folder or Path(__file__).parent / "data"
        )
        self._filename = filename
        self._delay = delay
        self._loaded_vocabularies = set()

    def _entry_points(self):
        """List entrypoints.

        Python now officially recommends importlib.metadata
        (importlib_metadata backport) for entrypoints:
        - https://docs.python.org/3/library/importlib.metadata.html
        - https://packaging.python.org/guides/creating-and-discovering-plugins/
          #using-package-metadata

        but Invenio is much invested in pkg_resources (``entry_points``
        fixture assumes it). So we use pkg_resources for now until
        _entry_points implementation can be changed.
        """
        return list(
            pkg_resources.iter_entry_points('invenio_rdm_records.fixtures')
        )

    def load(self):
        """Load the fixtures.

        Loads in priority

        1- app_data_folder
        2- extensions
        3- this package's fixtures

        Fixtures found later are ignored.
        """
        # Prime with existing (sub)vocabularies
        v_type_ids = [
            v.id for v in VocabularyType.query.options(load_only("id")).all()
        ]
        v_subtype_ids = [
            f"{v.parent_id}.{v.id}" for v in
            VocabularyScheme.query.options(
                load_only("id", "parent_id")
            ).all()
        ]
        self._loaded_vocabularies = set(v_type_ids + v_subtype_ids)

        # 1- Load from app_data_folder
        filepath = self._app_data_folder / self._filename
        # An instance doesn't necessarily have custom vocabularies
        # and that's ok
        if filepath.exists():
            self.load_vocabularies(filepath)

        # 2- Load from extensions / entry_points
        self.load_from_extensions()

        # 3- Load any default fixtures from invenio_rdm_records
        self.load_vocabularies(self._pkg_data_folder / self._filename)

    def load_from_extensions(self):
        """Load vocabularies from extensions.

        There might be priority conflicts at the extensions level. An
        exception is raised in this case rather than loading any fixture.
        """
        # First check if any conflicts
        vocabulary_modules = defaultdict(list)
        extensions = [ep.load() for ep in self._entry_points()]
        for module in extensions:
            directory = Path(module.__file__).parent
            filepath = directory / self._filename
            for v in self.peek_vocabularies(filepath):
                vocabulary_modules[v].append(module.__name__)

        errors = [
            f"Vocabulary '{v}' cannot have multiple sources {ms}"
            for v, ms in vocabulary_modules.items() if len(ms) > 1
        ]
        if errors:
            raise ConflictingOriginError(errors)

        # Then load
        for module in extensions:
            directory = Path(module.__file__).parent
            filepath = directory / self._filename
            self.load_vocabularies(filepath)

    def peek_vocabularies(self, filepath):
        """Peek at vocabularies listed in vocabularies file.

        Returns list of vocabularies.
        """
        vocabularies = []
        fixture = LocalImporter(self._identity, filepath)
        for id_, entry in fixture.read():
            vocabularies.extend(entry.covered_ids)
        return vocabularies

    def load_vocabularies(self, filepath):
        """Load vocabularies listed in vocabularies file."""
        fixture = LocalImporter(
            self._identity,
            filepath,
            delay=self._delay
        )
        self._loaded_vocabularies = fixture.load(
            ignore=self._loaded_vocabularies
        )
