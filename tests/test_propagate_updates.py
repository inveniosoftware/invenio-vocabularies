# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Propagate updates tests."""

import pytest
from invenio_db import db
from invenio_records_permissions.generators import AnyUser
from invenio_records_permissions.policies import \
    RecordPermissionPolicy as BaseRecordPermissionPolicy
from invenio_records_resources.services import RecordService, \
    RecordServiceConfig
from invenio_records_resources.services.records.components import DataComponent
from invenio_records_resources.services.records.schema import BaseRecordSchema
from marshmallow import Schema, fields
from marshmallow_utils.fields import SanitizedUnicode
from mock_module.api import Record

from invenio_vocabularies.records.api import Vocabulary
from invenio_vocabularies.records.models import VocabularyType
from invenio_vocabularies.services.components import RelationsComponent


@pytest.fixture(scope='module')
def app_config(app_config):
    """Mimic an instance's configuration."""
    app_config["JSONSCHEMAS_HOST"] = 'localhost'
    app_config["BABEL_DEFAULT_LOCALE"] = 'en'
    app_config["I18N_LANGUAGES"] = [('da', 'Danish')]
    app_config['RECORDS_REFRESOLVER_CLS'] = \
        "invenio_records.resolver.InvenioRefResolver"
    app_config['RECORDS_REFRESOLVER_STORE'] = \
        "invenio_jsonschemas.proxies.current_refresolver_store"
    app_config['INDEXER_DEFAULT_INDEX'] = "rdmrecords-records-record-v4.0.0"
    app_config['SQLALCHEMY_DATABASE_URI'] = \
        "postgresql+psycopg2://invenio:invenio@localhost:5432/invenio"

    return app_config


@pytest.fixture(scope="module")
def rec_service():

    class VocabularySchema(Schema):
        """Invenio Vocabulary schema."""

        id = SanitizedUnicode(required=True)
        title = fields.Dict(dump_only=True)

    class MetadataScheme(Schema):
        """Dummy metadata schema."""

        title = SanitizedUnicode(required=True)
        languages = fields.List(fields.Nested(VocabularySchema))

    class RecordSchema(BaseRecordSchema):
        """Dummy record schema."""

        _access = fields.Dict()
        owners = fields.List(fields.Number())
        metadata = fields.Nested(MetadataScheme)

    class RecordPermissionPolicy(BaseRecordPermissionPolicy):
        """Dummy record permission policy."""
        can_create = [AnyUser()]
        can_update = [AnyUser()]

    class ServiceCofig(RecordServiceConfig):
        """Service config with Record as record_cls."""

        permission_policy_cls = RecordPermissionPolicy
        record_cls = Record
        schema = RecordSchema
        components = [
            DataComponent,
            RelationsComponent,
        ]

    return RecordService(config=ServiceCofig)


@pytest.fixture(scope="module")
def vocab_service(app):
    return app.extensions['invenio-vocabularies'].service


@pytest.fixture(scope="module")
def lang_data():
    return {
        'id': 'eng',
        'title': {'en': 'English', 'da': 'Engelsk'},
        'description': {
            'en': 'English description',
            'da': 'Engelsk beskrivelse'
        },
        'icon': 'file-o',
        'props': {
            'akey': 'avalue',
        },
        'tags': ['recommended'],
        'type': 'languages',
    }


@pytest.fixture(scope="module")
def language_rec(identity, vocab_service, lang_data):

    # create vocabulary type
    _ = VocabularyType.create(id='languages', pid_type='lng')
    db.session.commit()
    lang_rec = vocab_service.create(identity, lang_data)
    Vocabulary.index.refresh()

    return lang_rec


def test_update_propagation_on_save(
    app, identity, rec_service, vocab_service, language_rec, lang_data
):
    """Test relation field records update propagation.

    It can be seen that:
    1. Updating the vocabulary (related) record is enought o get updates
       from DB reads, since the dereferencing is done by service components.
       The DB only contains the vocabulary id at all times.
    2. Updating the record would trigger an updated of the referenced fields
       in ES. Thus, a "re-index" of the touched records would suffice.
    """
    expected_lang = [{
        'id': 'eng',
        'title': {'en': 'English', 'da': 'Engelsk'}
    }]
    # create record with linked entries
    rec_data = {
        "_access": {"metadata_restricted": False,},
        "owners": [1],
        "metadata": {'title': 'Test', 'languages': [{'id': 'eng'}]}
    }
    init_rec = rec_service.create(identity, rec_data)
    id_ = init_rec.id

    # check record in db
    from_db = rec_service.read(identity, id_)
    assert from_db["metadata"]["languages"] == expected_lang

    # check record in es
    Record.index.refresh()
    from_es = rec_service.search(identity)
    assert from_es.total == 1
    from_es = list(from_es.hits)[0]
    assert from_es["metadata"]["languages"] == expected_lang

    ###### update lang vocabulary ######

    lang_data["title"]['es'] = "Ingles"
    up_lang = vocab_service.update(identity, ('languages', 'eng'), lang_data)
    assert "es" in up_lang.data["title"].keys()

    # check record in db still the same, it is NOT
    # because in db is only stored as id: [{'id': 'eng'}]
    # then the RelationsComponent dereferences on read
    from_db = rec_service.read(identity, id_)
    assert from_db["metadata"]["languages"][0]["title"] == {
        'en': 'English', 'da': 'Engelsk', 'es': 'Ingles'
    }

    # check record in es still the same
    from_es = rec_service.search(identity)
    assert from_es.total == 1
    from_es = list(from_es.hits)[0]
    assert from_es["metadata"]["languages"][0]["title"] == {
        'en': 'English', 'da': 'Engelsk'
    }

    ###### update record title ######

    # this will trigger a re-index of the related fields on ES
    rec_data["metadata"]["title"] = "Updated"
    expected_lang = [{
        'id': 'eng',
        'title': {'en': 'English', 'da': 'Engelsk', 'es': 'Ingles'}
    }]
    updated_rec = rec_service.update(identity, id_, rec_data)
    updated_rec.data["metadata"]["title"] == "Updated"
    updated_rec.data["metadata"]["languages"] == expected_lang

    # check record in db
    from_db = rec_service.read(identity, id_)
    assert from_db["metadata"]["languages"] == expected_lang

    # check record in es (should be like the old record)
    Record.index.refresh()
    from_es = rec_service.search(identity)
    assert from_es.total == 1
    from_es = list(from_es.hits)[0]
    assert from_es["metadata"]["languages"] == expected_lang


def test_update_propagation_reindexing(
    app, identity, rec_service, vocab_service, language_rec, lang_data
):
    """Test if reindexing records is not enough.

    The main problem with re-indexing is that the RecordService.reindex
    is passing an iterable of recids, while the indexer expects an iterable
    of UUIDs. See possible fixes in comments below.

    In addition, the RecordService.reindex triggers a reindex in the full
    collection of records. We might want to implement a "reindex_many".
    """
    expected_lang = [{
        'id': 'eng',
        'title': {'en': 'English', 'da': 'Engelsk'}
    }]
    # create record with linked entries
    rec_data = {
        "_access": {"metadata_restricted": False,},
        "owners": [1],
        "metadata": {'title': 'Test', 'languages': [{'id': 'eng'}]}
    }
    init_rec = rec_service.create(identity, rec_data)
    id_ = init_rec.id

    # check record in db
    from_db = rec_service.read(identity, id_)
    assert from_db["metadata"]["languages"] == expected_lang

    # check record in es
    Record.index.refresh()
    from_es = rec_service.search(identity)
    assert from_es.total == 1
    from_es = list(from_es.hits)[0]
    assert from_es["metadata"]["languages"] == expected_lang

    ###### update lang vocabulary ######

    lang_data["title"]['es'] = "Ingles"
    up_lang = vocab_service.update(identity, ('languages', 'eng'), lang_data)
    assert "es" in up_lang.data["title"].keys()

    # check record in db still the same, it is NOT
    # because in db is only stored as id: [{'id': 'eng'}]
    # then the RelationsComponent dereferences on read
    from_db = rec_service.read(identity, id_)
    assert from_db["metadata"]["languages"][0]["title"] == {
        'en': 'English', 'da': 'Engelsk', 'es': 'Ingles'
    }

    # check record in es still the same
    from_es = rec_service.search(identity)
    assert from_es.total == 1
    from_es = list(from_es.hits)[0]
    assert from_es["metadata"]["languages"][0]["title"] == {
        'en': 'English', 'da': 'Engelsk'
    }

    ###### re-index the record ######
    # we might want to add a query param to reindex only some ids
    _ = rec_service.reindex(identity)
    # force processing the bulk queue
    # note: for this to work, the indexer need to be fixed with respect to
    # the service.reindex function. The indexer.api expects a UUID as id,
    # while the service method is passing an iter of recids. This leads to
    # SQL exceptions. It can be fixed at service level or change the
    # `record_cls.get_record` call by `record_cls.pid.resolve`.

    # need to make customizable the invenio_indexer.task indexer obj
    rec_service.indexer.process_bulk_queue()

    expected_lang = [{
        'id': 'eng',
        'title': {'en': 'English', 'da': 'Engelsk', 'es': 'Ingles'}
    }]
    # check record in db
    from_db = rec_service.read(identity, id_)
    assert from_db["metadata"]["languages"] == expected_lang

    # check record in es (should be like the old record)
    Record.index.refresh()
    from_es = rec_service.search(identity)
    assert from_es.total == 1
    from_es = list(from_es.hits)[0]
    assert from_es["metadata"]["languages"] == expected_lang
