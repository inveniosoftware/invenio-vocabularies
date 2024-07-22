# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
# Copyright (C) 2024 KTH Royal Institute of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
"""Test VocabularyConfig."""

import pytest
from invenio_records_resources.proxies import current_service_registry

from invenio_vocabularies.contrib.affiliations.datastreams import (
    DATASTREAM_CONFIG as affiliations_ds_config,
)
from invenio_vocabularies.contrib.awards.datastreams import (
    DATASTREAM_CONFIG as awards_ds_config,
)
from invenio_vocabularies.contrib.funders.datastreams import (
    DATASTREAM_CONFIG as funders_ds_config,
)
from invenio_vocabularies.contrib.names.datastreams import (
    DATASTREAM_CONFIG as names_ds_config,
)
from invenio_vocabularies.factories import (
    AffiliationsVocabularyConfig,
    AwardsVocabularyConfig,
    FundersVocabularyConfig,
    NamesVocabularyConfig,
)


@pytest.mark.parametrize(
    "conf, ds_config, service_type",
    [
        (AwardsVocabularyConfig(), awards_ds_config, "awards-service"),
        (NamesVocabularyConfig(), names_ds_config, "names-service"),
        (FundersVocabularyConfig(), funders_ds_config, "funders-service"),
        (
            AffiliationsVocabularyConfig(),
            affiliations_ds_config,
            "affiliations-service",
        ),
    ],
)
def test_vocabulary_config(conf, ds_config, service_type, app):
    """Test VocabularyConfig."""
    config = conf.get_config()

    # Compare readers
    assert config["readers"] == ds_config["readers"]

    # Compare writers, excluding 'identity'
    for config_writer, expected_writer in zip(config["writers"], ds_config["writers"]):
        assert config_writer["type"] == expected_writer["type"]
        assert str(config_writer["args"]) == str(expected_writer["args"])
        if config["writers"][0]["type"] == "async":
            assert config["writers"][0]["args"]["writer"]["type"] == service_type
        else:
            assert config["writers"][0]["type"] == service_type


def test_names_service(app):
    """Test service retrieval for names."""
    names_conf = NamesVocabularyConfig()
    service = names_conf.get_service()
    assert service == current_service_registry.get("names")


@pytest.mark.parametrize(
    "config_class, expected_error",
    [
        (FundersVocabularyConfig, NotImplementedError),
        (AwardsVocabularyConfig, NotImplementedError),
    ],
)
def test_service_not_implemented(config_class, expected_error, app):
    """Test services that are not implemented."""
    with pytest.raises(expected_error):
        conf = config_class()
        conf.get_service()
