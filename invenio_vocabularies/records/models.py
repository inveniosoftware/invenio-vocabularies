# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary models."""

from invenio_db import db
from invenio_records.models import RecordMetadataBase


class VocabularyType(db.Model):
    """Vocabulary type model."""

    __tablename__ = "vocabularies_types"

    id = db.Column(db.String, primary_key=True)
    pid_type = db.Column(db.String, unique=True)

    @classmethod
    def create(cls, **data):
        """Create a new vocabulary type."""
        with db.session.begin_nested():
            obj = cls(**data)
            db.session.add(obj)
        return obj

    @classmethod
    def dump_obj(cls, field, record, obj):
        """Serializer the object into a record."""
        record[field.attr_name] = {
            'id': obj.id,
            'pid_type': obj.pid_type,
        }

    @classmethod
    def load_obj(cls, field, record):
        """Deserializer the object from a record."""
        data = record.get(field.attr_name)
        if data:
            obj = cls(
                id=data.get('id'),
                pid_type=data.get('pid_type'),
            )
            return obj
        return None


class VocabularyMetadata(db.Model, RecordMetadataBase):
    """Model for vocabulary metadata."""

    __tablename__ = "vocabularies_metadata"


class VocabularySubtype(db.Model):
    """Vocabulary subtype type model.

    Current use case is for subject types.
    """

    __tablename__ = "vocabularies_subtypes"

    id = db.Column(db.String, primary_key=True)
    # pid_type = db.Column(db.String, unique=True)
    vocabulary_id = db.Column(
        db.String,
        db.ForeignKey(VocabularyType.id, ondelete='CASCADE'),
        nullable=False,
    )
    label = db.Column(db.String)
    prefix_url = db.Column(db.String)

    """Any extra metadata."""

    @classmethod
    def create(cls, **data):
        """Create a new vocabulary subtype."""
        with db.session.begin_nested():
            obj = cls(**data)
            db.session.add(obj)
        return obj
