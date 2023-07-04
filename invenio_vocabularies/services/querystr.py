# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Querystring parsing."""

from functools import partial

from invenio_records_resources.services.records.params import SuggestQueryParser
from invenio_search.engine import dsl


class FilteredSuggestQueryParser(SuggestQueryParser):
    """Query parser for filtered search-as-you-type/auto completion."""

    @classmethod
    def factory(cls, filter_field=None, **extra_params):
        """Create a prepared instance of the query parser."""
        return partial(cls, filter_field=filter_field, extra_params=extra_params)

    def __init__(self, identity=None, filter_field=None, extra_params=None):
        """Constructor."""
        super().__init__(identity=identity, extra_params=extra_params)
        self.filter_field = filter_field

    def parse(self, query_str):
        """Parse the query."""
        subtype_s, query_str = self.extract_subtype_s(query_str)
        query = super().parse(query_str)
        if subtype_s:
            query = query & dsl.Q("terms", **{self.filter_field: subtype_s})
        return query

    def extract_subtype_s(self, query_str):
        """Extract the filtering subtype(s) from query_str.

        Return (<subtypes>, <rest of original query string>).
        """
        parts = query_str.split(":", 1)
        if len(parts) == 1:
            subtypes = []
            rest_query_str = query_str
        else:
            # Simplification: we can enforce no comma in subtype at
            #                 subtype creation
            subtypes = parts[0].split(",")
            rest_query_str = parts[1]
        return (subtypes, rest_query_str)
