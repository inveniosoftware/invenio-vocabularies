# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Names services."""

from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_search.engine import dsl

from .names import record_type

NamesServiceConfig = record_type.service_config_cls


class NamesService(record_type.service_cls):
    """Name service."""

    def resolve(self, identity, id_, id_type, many=False):
        """Get the record with a given identifier.

        param id_: The identifier value.
        param id_type: The identifier type.
        param many: If True, return a list of records.
        """
        search_query = dsl.Q(
            "bool",
            minimum_should_match=1,
            must=[
                dsl.Q("term", identifiers__identifier=id_),
                dsl.Q("term", identifiers__scheme=id_type),
            ],
        )

        # max_records = 1, we assume there cannot be duplicates
        # the loading process needs to make sure of that
        if many:
            results = self._read_many(identity, search_query)
        else:
            results = self._read_many(identity, search_query, max_records=1)

        # cant use the results_item because it returns dicts instead of records
        total = results.hits.total["value"]
        if total == 0:
            # Not a PID but treated as such
            raise PIDDoesNotExistError(pid_type=id_type, pid_value=id_)
        if many:
            for result in results:
                record = self.record_cls.loads(result.to_dict())
                self.require_permission(identity, "read", record=record)
            return self.result_list(self, identity, results)
        else:
            record = self.record_cls.loads(results[0].to_dict())
            self.require_permission(identity, "read", record=record)

            return self.result_item(
                self,
                identity,
                record,
                links_tpl=self.links_item_tpl,
            )
