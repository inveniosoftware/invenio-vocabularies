# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary service."""

from invenio_db import db
from invenio_records_resources.services import RecordService, \
    RecordServiceConfig
from invenio_records_resources.services.records.components import DataComponent
from invenio_records_resources.services.records.params import FilterParam
from invenio_records_resources.services.records.search import terms_filter
from marshmallow.exceptions import ValidationError

from invenio_vocabularies.records.models import VocabularyType

from ..records.api import Vocabulary
from .components import PIDComponent, VocabularyTypeComponent
from .permissions import PermissionPolicy
from .schema import VocabularySchema


class VocabulariesServiceConfig(RecordServiceConfig):
    """Vocabulary service configuration."""

    permission_policy_cls = PermissionPolicy
    record_cls = Vocabulary
    schema = VocabularySchema

    search_params_interpreters_cls = [
        FilterParam.factory(param='type', field='type.id'),
        FilterParam.factory(param='tags', field='tags'),
    ] + RecordServiceConfig.search_params_interpreters_cls

    components = [
        # Order of component is important!
        VocabularyTypeComponent,
        DataComponent,
        PIDComponent,
    ]


class VocabulariesService(RecordService):
    """Vocabulary service."""

    default_config = VocabulariesServiceConfig

    def create_type(self, identity, id, pid_type):
        """Create a new vocabulary type."""
        self.require_permission(identity, "manage")
        type_ = VocabularyType.create(id=id, pid_type=pid_type)
        db.session.commit()
        return type_

    def search_request(self, identity, params, record_cls, preference=None):
        """Create a search request.

        This method just ensures that the vocabulary type is validated.
        """
        # Validate type parameter
        if 'type' in params:
            # If not found, NoResultFound is raised (caught by the resource).
            vocabulary_type = VocabularyType.query.filter_by(
                id=params['type']).one()
            # Pass the type so it's available for link generation
            params['_type'] = vocabulary_type
        return super().search_request(
            identity, params, record_cls, preference=preference)
