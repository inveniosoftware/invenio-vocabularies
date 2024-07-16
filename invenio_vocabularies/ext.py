# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 CERN.
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio module for managing vocabularies."""

from . import config
from .contrib.affiliations import (
    AffiliationsResource,
    AffiliationsResourceConfig,
    AffiliationsService,
    AffiliationsServiceConfig,
)
from .contrib.awards import (
    AwardsResource,
    AwardsResourceConfig,
    AwardsService,
    AwardsServiceConfig,
)
from .contrib.funders import (
    FundersResource,
    FundersResourceConfig,
    FundersService,
    FundersServiceConfig,
)
from .contrib.names import (
    NamesResource,
    NamesResourceConfig,
    NamesService,
    NamesServiceConfig,
)
from .contrib.subjects import (
    SubjectsResource,
    SubjectsResourceConfig,
    SubjectsService,
    SubjectsServiceConfig,
)
from .resources import (
    VocabulariesAdminResource,
    VocabulariesResource,
    VocabulariesResourceConfig,
    VocabularyTypeResourceConfig,
)
from .services.config import VocabularyTypesServiceConfig
from .services.service import VocabulariesService, VocabularyTypeService


class InvenioVocabularies(object):
    """Invenio-Vocabularies extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        self.resource = None
        self.service = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.init_services(app)
        self.init_resource(app)
        app.extensions["invenio-vocabularies"] = self

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("VOCABULARIES_"):
                app.config.setdefault(k, getattr(config, k))

    def service_configs(self, app):
        """Customized service configs."""

        class ServiceConfigs:
            affiliations = AffiliationsServiceConfig
            awards = AwardsServiceConfig
            funders = FundersServiceConfig
            names = NamesServiceConfig
            subjects = SubjectsServiceConfig
            vocabulary_types = VocabularyTypesServiceConfig

        return ServiceConfigs

    def init_services(self, app):
        """Initialize vocabulary resources."""
        service_configs = self.service_configs(app)

        # Services
        self.affiliations_service = AffiliationsService(
            config=service_configs.affiliations,
        )
        self.awards_service = AwardsService(
            config=service_configs.awards,
        )
        self.funders_service = FundersService(config=service_configs.funders)
        self.names_service = NamesService(config=service_configs.names)
        self.subjects_service = SubjectsService(config=service_configs.subjects)
        self.vocabularies_service = VocabulariesService(
            config=app.config["VOCABULARIES_SERVICE_CONFIG"],
        )
        self.vocabulary_types_service = VocabularyTypeService(
            config=service_configs.vocabulary_types
        )

    def init_resource(self, app):
        """Initialize vocabulary resources."""
        # Generic Vocabularies
        self.affiliations_resource = AffiliationsResource(
            service=self.affiliations_service,
            config=AffiliationsResourceConfig,
        )
        self.funders_resource = FundersResource(
            service=self.funders_service,
            config=FundersResourceConfig,
        )
        self.names_resource = NamesResource(
            service=self.names_service,
            config=NamesResourceConfig,
        )
        self.awards_resource = AwardsResource(
            service=self.awards_service,
            config=AwardsResourceConfig,
        )
        self.subjects_resource = SubjectsResource(
            service=self.subjects_service,
            config=SubjectsResourceConfig,
        )
        self.resource = VocabulariesResource(
            service=self.vocabularies_service,
            config=app.config["VOCABULARIES_RESOURCE_CONFIG"],
        )
        self.vocabulary_admin_resource = VocabulariesAdminResource(
            service=self.vocabulary_types_service,
            config=VocabularyTypeResourceConfig,
        )


def finalize_app(app):
    """Finalize app.

    NOTE: replace former @record_once decorator
    """
    init(app)


def api_finalize_app(app):
    """Api Finalize app.

    NOTE: replace former @record_once decorator
    """
    init(app)


def init(app):
    """Init app."""
    # Register services - cannot be done in extension because
    # Invenio-Records-Resources might not have been initialized.
    sregistry = app.extensions["invenio-records-resources"].registry
    ext = app.extensions["invenio-vocabularies"]
    sregistry.register(ext.affiliations_service, service_id="affiliations")
    sregistry.register(ext.awards_service, service_id="awards")
    sregistry.register(ext.funders_service, service_id="funders")
    sregistry.register(ext.names_service, service_id="names")
    sregistry.register(ext.subjects_service, service_id="subjects")
    sregistry.register(ext.vocabularies_service, service_id="vocabularies")
    sregistry.register(ext.vocabulary_types_service, service_id="vocabulary-types")
    # Register indexers
    iregistry = app.extensions["invenio-indexer"].registry
    iregistry.register(ext.affiliations_service.indexer, indexer_id="affiliations")
    iregistry.register(ext.awards_service.indexer, indexer_id="awards")
    iregistry.register(ext.funders_service.indexer, indexer_id="funders")
    iregistry.register(ext.names_service.indexer, indexer_id="names")
    iregistry.register(ext.subjects_service.indexer, indexer_id="subjects")
    iregistry.register(ext.vocabularies_service.indexer, indexer_id="vocabularies")
