# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Funders schema."""

from flask_babelex import lazy_gettext as _
from marshmallow import Schema, fields, validate
from marshmallow_utils.fields import SanitizedUnicode


class FunderRelationSchema(Schema):
    """Funder schema."""

    name = SanitizedUnicode(
        required=True,
        validate=validate.Length(min=1, error=_('Name cannot be blank.'))
    )
    scheme = SanitizedUnicode()
    identifier = SanitizedUnicode()
