#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2022-2023 Graz University of Technology.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

# Quit on errors
set -o errexit

# Quit on unbound symbols
set -o nounset

# Always bring down docker services
function cleanup {
    eval "$(docker-services-cli down --env)"
}
trap cleanup EXIT

python -m check_manifest
python -m setup extract_messages --output-file /dev/null
python -m sphinx.cmd.build -qnNW docs docs/_build/html
eval "$(docker-services-cli up --db ${DB:-postgresql} --search ${ES:-opensearch} --mq ${CACHE:-redis} --env)"
python -m pytest $@
tests_exit_code=$?
exit "$tests_exit_code"
