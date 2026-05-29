# SPDX-FileCopyrightText: 2021-2022 CERN.
# SPDX-FileCopyrightText: 2024 California Institute of Technology.
# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Funders schema."""

from invenio_i18n import lazy_gettext as _
from marshmallow import (
    fields,
    validate,
)
from marshmallow_utils.fields import IdentifierSet, SanitizedUnicode
from marshmallow_utils.schemas import IdentifierSchema

from ...services.schema import (
    BaseVocabularySchema,
    ContribVocabularyRelationSchema,
    ModePIDFieldVocabularyMixin,
)
from .config import funder_schemes


class FunderRelationSchema(ContribVocabularyRelationSchema):
    """Funder schema."""

    ftf_name = "name"
    parent_field_name = "funder"
    name = SanitizedUnicode(
        validate=validate.Length(min=1, error=_("Name cannot be blank."))
    )


class FunderSchema(BaseVocabularySchema, ModePIDFieldVocabularyMixin):
    """Service schema for funders."""

    name = SanitizedUnicode(
        required=True, validate=validate.Length(min=1, error=_("Name cannot be blank."))
    )
    country = SanitizedUnicode()
    country_name = SanitizedUnicode()
    location_name = SanitizedUnicode()
    identifiers = IdentifierSet(
        fields.Nested(
            IdentifierSchema(allowed_schemes=funder_schemes, identifier_required=False)
        )
    )

    id = SanitizedUnicode(
        validate=validate.Length(min=1, error=_("PID cannot be blank."))
    )

    acronym = SanitizedUnicode()
    aliases = fields.List(SanitizedUnicode())
    status = SanitizedUnicode()
    types = fields.List(SanitizedUnicode())
