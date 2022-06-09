# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names services."""

from elasticsearch_dsl.query import Q
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records_resources.config import lt_es7

from .names import record_type

NamesServiceConfig = record_type.service_config_cls


class NamesService(record_type.service_cls):
    """Name service."""

    def resolve(self, identity, id_, id_type):
        """Get the record with a given identifier.

        This method assumes that the are no duplicates in the system
        (i.e. only one name record can have a pair of identifier:scheme).
        """
        es_query = Q(
            "bool",
            minimum_should_match=1,
            must=[
                Q("term", identifiers__identifier=id_),
                Q("term", identifiers__scheme=id_type),
            ],
        )

        # max_records = 1, we assume there cannot be duplicates
        # the loading process needs to make sure of that
        results = self._read_many(identity, es_query, max_records=1)
        # cant use the results_item because it returns dicts intead of records
        total = results.hits.total if lt_es7 else results.hits.total["value"]
        if total == 0:
            # Not a PID but trated as such
            raise PIDDoesNotExistError(pid_type=id_type, pid_value=id_)

        # (0 < #hits <= max_records) = 1
        record = self.record_cls.loads(results[0].to_dict())
        self.require_permission(identity, "read", record=record)

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
        )
