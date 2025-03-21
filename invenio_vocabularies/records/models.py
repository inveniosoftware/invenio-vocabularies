# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary models."""

from invenio_db import db
from invenio_i18n import gettext as _
from invenio_records.models import RecordMetadataBase


class VocabularyType(db.Model):
    """Vocabulary type model."""

    __tablename__ = "vocabularies_types"

    id = db.Column(db.String(255), primary_key=True)
    pid_type = db.Column(db.String(255), unique=True)

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
            "id": obj.id,
            "pid_type": obj.pid_type,
        }

    @classmethod
    def load_obj(cls, field, record):
        """Deserializer the object from a record."""
        data = record.get(field.attr_name)
        if data:
            obj = cls(
                id=data.get("id"),
                pid_type=data.get("pid_type"),
            )
            return obj
        return None


class VocabularyMetadata(db.Model, RecordMetadataBase):
    """Model for vocabulary metadata."""

    __tablename__ = "vocabularies_metadata"


class VocabularyScheme(db.Model):
    """Vocabulary scheme model.

    This table stores the metadata for schemes (subtypes) of VocabularyType
    or separate specific vocabularies.

    It is only used to store metadata for subject schemes for now.
    But we might store affiliations's schemes or other schemes later.
    """

    __tablename__ = "vocabularies_schemes"

    id = db.Column(db.String(255), primary_key=True)
    # This is e.g. `subjects`, 'affiliations', ...
    parent_id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255))
    uri = db.Column(db.String(255))
    # Any extra metadata is added as columns.

    @classmethod
    def create(cls, **data):
        """Create a new vocabulary subtype."""
        banned = [",", ":"]
        for b in banned:
            assert b not in data["id"], _(
                "No '%(banned_char)s' allowed in VocabularyScheme.id", banned_char=b
            )

        with db.session.begin_nested():
            obj = cls(**data)
            db.session.add(obj)
        return obj
