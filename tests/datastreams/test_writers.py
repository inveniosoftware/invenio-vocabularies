# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Data Streams writers tests."""

from invenio_vocabularies.datastreams.writers import ServiceWriter


def test_service_writer(lang_type, lang_data, service, identity):
    writer = ServiceWriter(service, identity)
    lang = writer.write(entry=lang_data)
    record = service.read(("languages", lang.id), identity)
    record = record.to_dict()

    assert dict(record, **lang_data) == record
