# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Record serializers."""
import json

from flask_resources.serializers import JSONSerializer

from invenio_vocabularies.resources.records.serializers.schema import \
    PresentationVocabularyListSchema, PresentationVocabularySchema


class PresentationJSONSerializer(JSONSerializer):
    """JSON serializer implementation."""

    object_schema_cls = PresentationVocabularySchema
    list_schema_cls = PresentationVocabularyListSchema

    def dump_obj(self, obj):
        """Dump the object with extra information."""
        return self.object_schema_cls().dump(obj)

    def dump_list(self, obj_list):
        """Dump the list of objects with extra information."""
        ctx = {
            'object_schema_cls': self.object_schema_cls,
        }
        return self.list_schema_cls(context=ctx).dump(obj_list)

    def serialize_object(self, obj):
        """Dump the object into a JSON string."""
        return json.dumps(self.dump_obj(obj))

    def serialize_object_list(self, obj_list):
        """Dump the object list into a JSON string."""
        return json.dumps(self.dump_list(obj_list))

    def serialize_object_to_dict(self, obj):
        """Dump the object into a JSON string."""
        return self.dump_obj(obj)

    def serialize_object_list_to_dict(self, obj_list):
        """Dump the object list into a JSON string."""
        return self.dump_list(obj_list)
