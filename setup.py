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
    # "invenio-search[elasticsearch7]>=1.4.1,<2.0.0",
    "pytest-invenio>=1.4.0",
]

# Should follow inveniosoftware/invenio versions
invenio_search_version = ">=1.4.1,<2.0.0"
invenio_db_version = ">=1.0.5,<2.0.0"

extras_require = {
    "docs": [
        "Sphinx>=3",
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
    "invenio-i18n>=1.2.0",
    "invenio-records-resources>=0.8.7",
    "invenio-pidstore>=1.2.1",
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
    keywords="invenio TODO",
    license="MIT",
    author="CERN",
    author_email="info@inveniosoftware.org",
    url="https://github.com/inveniosoftware/invenio-vocabularies",
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    entry_points={
        "console_scripts": [
            "vocabularies = invenio_app.cli:cli",
        ],
        "invenio_base.apps": [
            "invenio_vocabularies = invenio_vocabularies:InvenioVocabularies",
        ],
        "invenio_base.api_apps": [
            "invenio_vocabularies = invenio_vocabularies:InvenioVocabularies",
        ],
        "flask.commands": [
            "load = invenio_vocabularies.cli:load",
        ],
        "invenio_config.module": [
            "invenio_vocabularies = invenio_vocabularies.config",
        ],
        "invenio_db.model": [
            "vocabulary_model = invenio_vocabularies.vocabularies.models",
        ],
        "invenio_i18n.translations": [
            "messages = invenio_vocabularies",
        ],
        "invenio_jsonschemas.schemas": [
            "jsonschemas = invenio_vocabularies.jsonschemas",
        ],
        "invenio_search.mappings": [
            "vocabularies = invenio_vocabularies.mappings",
        ],
        # TODO: See which of the following we truly need
        # 'invenio_assets.bundles': [],
        # 'invenio_base.api_blueprints': [],
        # 'invenio_base.blueprints': [],
        # 'invenio_celery.tasks': [],
        # 'invenio_db.models': [],
        # 'invenio_pidstore.minters': [],
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
        "Development Status :: 1 - Planning",
    ],
)
