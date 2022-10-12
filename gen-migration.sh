#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Northwestern University.
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

if [[ "$#" -ne 2 ]]; then
    echo "Usage: ./gen-migration.sh <parent_id> <revision msg>"
fi

parent_id=$1
message=$2

eval "$(docker-services-cli up --db ${DB:-postgresql} --search ${ES:-opensearch} --mq ${CACHE:-redis} --env)"
export INVENIO_SQLALCHEMY_DATABASE_URI=${SQLALCHEMY_DATABASE_URI}
invenio db drop --yes-i-know
invenio alembic upgrade
invenio alembic revision -p ${parent_id} "${message}"
# TODO: Automate this last part
echo "Now just extract path from output and move it to invenio_vocabularies/alembic/"
# sed Generating <path>" and; mv <path in output> invenio_vocabularies/alembic/
