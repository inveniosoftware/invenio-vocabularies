# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary models."""

from invenio_db import db
from invenio_records.models import RecordMetadataBase


class VocabularyType(db.Model):
    """Vocabulary type model."""

    __tablename__ = "vocabulary_type"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class VocabularyMetadata(db.Model, RecordMetadataBase):
    """Model for vocabulary metadata."""

    __tablename__ = "vocabularies_metadata"

    pid = db.Column(db.String)
    vocabulary_type = db.Column(
        db.Integer, db.ForeignKey("vocabulary_type.id")
    )
