# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Vocabulary affiliations."""

from elasticsearch_dsl.query import Q

from .funders import record_type

FundersServiceConfig = record_type.service_config_cls


class FundersService(record_type.service_cls):
    """Funders service."""

    def read_many(self, identity, ids, fields=None, **kwargs):
        """Search for records matching the ids."""
        clauses = []
        for id_ in ids:
            clauses.append(Q('term', **{"pid": id_}))
        query = Q('bool', minimum_should_match=1, should=clauses)

        results = self._read_many(
            identity, query, fields, len(ids), **kwargs)

        return self.result_list(self, identity, results)
