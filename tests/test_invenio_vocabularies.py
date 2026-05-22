# SPDX-FileCopyrightText: 2020 CERN.
# SPDX-License-Identifier: MIT

"""Module tests."""

from flask import Flask

from invenio_vocabularies import InvenioVocabularies


def test_version():
    """Test version import."""
    from invenio_vocabularies import __version__

    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask("testapp")
    ext = InvenioVocabularies(app)
    assert "invenio-vocabularies" in app.extensions

    app = Flask("testapp")
    ext = InvenioVocabularies()
    assert "invenio-vocabularies" not in app.extensions
    ext.init_app(app)
    assert "invenio-vocabularies" in app.extensions
