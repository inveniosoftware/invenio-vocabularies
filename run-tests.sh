#!/usr/bin/env sh
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.


# TODO: Pass the services required by your module to the
# docker-services-cli e.g. `docker-services-cli up es postgresql redis`
# remove docker-services-cli if you don't need any of the services.
docker-services-cli up && \
python -m check_manifest --ignore ".travis-*" && \
python -m sphinx.cmd.build -qnNW docs docs/_build/html && \
python -m pytest
python -m sphinx.cmd.build -qnNW -b doctest docs docs/_build/doctest
tests_exit_code=$?
docker-services-cli down
exit "$tests_exit_code"
