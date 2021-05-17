# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio module for managing vocabularies."""

import os

from setuptools import find_packages, setup

readme = open("README.rst").read()
history = open("CHANGES.rst").read()

tests_require = [
    "invenio-app>=1.3.0",
    "pytest-invenio>=1.4.1",
]

# Should follow inveniosoftware/invenio versions
invenio_search_version = ">=1.4.1,<2.0.0"
invenio_db_version = ">=1.0.9,<2.0.0"

extras_require = {
    "docs": [
        "Sphinx>=3,<4",
    ],
    "elasticsearch6": [
        "invenio-search[elasticsearch6]{}".format(invenio_search_version),
    ],
    "elasticsearch7": [
        "invenio-search[elasticsearch7]{}".format(invenio_search_version),
    ],
    # Databases
    "mysql": [
        "invenio-db[mysql,versioning]{}".format(invenio_db_version),
    ],
    "postgresql": [
        "invenio-db[postgresql,versioning]{}".format(invenio_db_version),
    ],
    "sqlite": [
        "invenio-db[versioning]{}".format(invenio_db_version),
    ],
    "tests": tests_require,
}

all_requires = []
for key, reqs in extras_require.items():
    if key in {"elasticsearch6", "elasticsearch7"}:
        continue
    all_requires.extend(reqs)
extras_require["all"] = all_requires

setup_requires = [
    "Babel>=2.8",
]

install_requires = [
    "flask>=1.1,<2",
    "invenio-records-resources>=0.15.1,<0.16.0",
    "invenio-i18n>=1.3.0",
]

packages = find_packages()

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("invenio_vocabularies", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

setup(
    name="invenio-vocabularies",
    version=version,
    description=__doc__,
    long_description=readme + "\n\n" + history,
    keywords="invenio vocabulary management",
    license="MIT",
    author="CERN",
    author_email="info@inveniosoftware.org",
    url="https://github.com/inveniosoftware/invenio-vocabularies",
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    entry_points={
        "flask.commands": [
            "vocabularies = invenio_vocabularies.cli:vocabularies",
        ],
        "invenio_base.apps": [
            "invenio_vocabularies = invenio_vocabularies:InvenioVocabularies",
        ],
        "invenio_base.api_apps": [
            "invenio_vocabularies = invenio_vocabularies:InvenioVocabularies",
        ],
        "invenio_base.api_blueprints": [
            'invenio_vocabularies = invenio_vocabularies.views:create_blueprint_from_app',
        ],
        "invenio_db.alembic": [
            "invenio_vocabularies = invenio_vocabularies:alembic",
        ],
        "invenio_db.models": [
            "vocabulary_model = invenio_vocabularies.records.models",
        ],
        "invenio_jsonschemas.schemas": [
            "jsonschemas = invenio_vocabularies.records.jsonschemas",
        ],
        "invenio_search.mappings": [
            "vocabularies = invenio_vocabularies.records.mappings",
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 3 - Alpha",
    ],
)
