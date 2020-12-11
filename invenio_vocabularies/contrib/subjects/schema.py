from marshmallow import EXCLUDE, INCLUDE, Schema, fields, \
    validate
from marshmallow_utils.fields import Links


class MetadataSchema(Schema):
    """Basic metadata schema class."""

    class Meta:
        """Meta class to accept unknown fields."""

        unknown = INCLUDE

    scheme = fields.Str(required=True, validate=validate.Length(min=3))
    term = fields.Str(required=True, validate=validate.Length(min=3))
    identifier = fields.Str(required=True, validate=validate.Length(min=3))
    scheme = fields.Str(required=True, validate=validate.Length(min=3))


class SubjectSchema(Schema):
    """Schema for records v1 in JSON."""

    class Meta:
        """Meta class to reject unknown fields."""

        unknown = EXCLUDE

    id = fields.Str()
    metadata = fields.Nested(MetadataSchema)
    created = fields.Str()
    updated = fields.Str()
    links = Links()
    revision_id = fields.Integer(dump_only=True)
