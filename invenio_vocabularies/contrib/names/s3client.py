# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2024-2025 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""S3 client."""

from flask import current_app

try:
    import s3fs
except ImportError:
    s3fs = None


class S3Client:
    """S3 client."""

    def __init__(self, access_key, secret_key):
        """Constructor."""
        if s3fs is None:
            raise Exception("s3fs is not installed.")

        self.fs = s3fs.S3FileSystem(key=access_key, secret=secret_key)

    def read_file(self, s3_path):
        """Reads a file from S3."""
        with self.fs.open(s3_path, "rb") as f:
            return f.read()


class S3OrcidClient(S3Client):
    """S3 ORCiD client."""

    def __init__(self):
        """Constructor."""
        access_key = current_app.config["VOCABULARIES_ORCID_ACCESS_KEY"]
        secret_key = current_app.config["VOCABULARIES_ORCID_SECRET_KEY"]
        if access_key == "CHANGEME" or secret_key == "CHANGEME":
            raise Exception(
                "VOCABULARIES_ORCID_ACCESS_KEY and VOCABULARIES_ORCID_SECRET_KEY are not configured."
            )
        super().__init__(
            access_key=access_key,
            secret_key=secret_key,
        )
