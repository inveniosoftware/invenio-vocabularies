# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 KTH Royal Institute of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
"""Generate Vocabulary Config."""

from copy import deepcopy

import yaml
from invenio_records_resources.proxies import current_service_registry

from .contrib.affiliations.datastreams import (
    DATASTREAM_CONFIG as affiliations_ds_config,
)
from .contrib.affiliations.datastreams import (
    DATASTREAM_CONFIG_OPENAIRE as affiliations_openaire_ds_config,
)
from .contrib.awards.datastreams import DATASTREAM_CONFIG as awards_ds_config
from .contrib.awards.datastreams import (
    DATASTREAM_CONFIG_CORDIS as awards_cordis_ds_config,
)
from .contrib.funders.datastreams import DATASTREAM_CONFIG as funders_ds_config
from .contrib.names.datastreams import DATASTREAM_CONFIG as names_ds_config
from .contrib.subjects.datastreams import DATASTREAM_CONFIG as subjects_ds_config


class VocabularyConfig:
    """Vocabulary Config Factory."""

    config = None
    vocabulary_name = None

    def get_config(self, filepath=None, origin=None):
        """Get the configuration for the vocabulary."""
        config = deepcopy(self.config)
        if filepath:
            with open(filepath, encoding="utf-8") as f:
                config = yaml.safe_load(f).get(self.vocabulary_name)
        if origin:
            config["readers"][0].setdefault("args", {})
            config["readers"][0]["args"]["origin"] = origin
        return config

    def get_service(self):
        """Get the service for the vocabulary."""
        return current_service_registry.get(self.vocabulary_name)


class NamesVocabularyConfig(VocabularyConfig):
    """Names Vocabulary Config."""

    config = names_ds_config
    vocabulary_name = "names"


class FundersVocabularyConfig(VocabularyConfig):
    """Funders Vocabulary Config."""

    config = funders_ds_config
    vocabulary_name = "funders"

    def get_service(self):
        """Get the service for the vocabulary."""
        raise NotImplementedError("Service not implemented for Funders")


class SubjectsVocabularyConfig(VocabularyConfig):
    """Subjects Vocabulary Config."""

    config = subjects_ds_config
    vocabulary_name = "subjects"

    def get_service(self):
        """Get the service for the vocabulary."""
        raise NotImplementedError("Service not implemented for Subjects")


class AwardsVocabularyConfig(VocabularyConfig):
    """Awards Vocabulary Config."""

    config = awards_ds_config
    vocabulary_name = "awards"

    def get_service(self):
        """Get the service for the vocabulary."""
        raise NotImplementedError("Service not implemented for Awards")


class AwardsCordisVocabularyConfig(VocabularyConfig):
    """Awards Vocabulary Config."""

    config = awards_cordis_ds_config
    vocabulary_name = "awards:cordis"

    def get_service(self):
        """Get the service for the vocabulary."""
        raise NotImplementedError("Service not implemented for CORDIS Awards")


class AffiliationsVocabularyConfig(VocabularyConfig):
    """Affiliations Vocabulary Config."""

    config = affiliations_ds_config
    vocabulary_name = "affiliations"

    def get_service(self):
        """Get the service for the vocabulary."""
        raise NotImplementedError("Service not implemented for Affiliations")


class AffiliationsOpenAIREVocabularyConfig(VocabularyConfig):
    """OpenAIRE Affiliations Vocabulary Config."""

    config = affiliations_openaire_ds_config
    vocabulary_name = "affiliations:openaire"

    def get_service(self):
        """Get the service for the vocabulary."""
        raise NotImplementedError("Service not implemented for OpenAIRE Affiliations")


def get_vocabulary_config(vocabulary):
    """Factory function to get the appropriate Vocabulary Config."""
    vocab_config = {
        "names": NamesVocabularyConfig,
        "funders": FundersVocabularyConfig,
        "awards": AwardsVocabularyConfig,
        "awards:cordis": AwardsCordisVocabularyConfig,
        "affiliations": AffiliationsVocabularyConfig,
        "affiliations:openaire": AffiliationsOpenAIREVocabularyConfig,
        "subjects": SubjectsVocabularyConfig,
    }
    return vocab_config.get(vocabulary, VocabularyConfig)()
