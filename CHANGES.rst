..
    Copyright (C) 2020-2024 CERN.
    Copyright (C) 2024 Graz University of Technology.

    Invenio-Vocabularies is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======

Version v7.5.0 (released 2025-06-03)

- jobs: ORCID job update instead of import (insert-only)
- readers: add SPARQLReader client params to allow setting user_agent (#472)
- chore(i18n): removed deprecated languages from i18next
- chore(tests): update MANIFEST.in
- chore(i18n): init catalog & extract messages
- refactor(i18n): use vocabularies i18next for funding ui
- config: update idutils imports
- logging: add basic logging for ROR HTTP reader
- names: ORCID Public Data Sync: detect default keys

Version v7.4.0 (released 2025-04-28)

- i18n: Fix untranslated strings in vocabularies
- logging: add basic logging for ORCID

Version v7.3.0 (released 2025-03-18)

- form: funding: use FeedbackLabel and add error styling

Version v7.2.1 (released 2025-03-17)

- subjects: Keep bool_prefix clause for suggest search

Version v7.2.0 (released 2025-03-10)

- search: fix too many clauses on affiliation search
- search: remove redundant fields from affiliation and funders search
- nvs subjects: fix deprecated subjects skipping (raise skipped)

Version v7.1.0 (released 2025-02-20)

- subjects: renamed bodc to nvs
- bodc: updated file uri & subject label

Version v7.0.0 (released 2025-02-13)

- Promote to stable release
- jobs: apply code upgrades

Version v7.0.0.dev2 (released 2025-01-23)

Version v7.0.0.dev1 (released 2024-12-12)

- comp: make compatible to flask-sqlalchemy>=3.1
- setup: change to reusable workflows
- setup: bump major dependencies

Version v6.11.0 (released 2024-12-13)

- names: fix acronym in marshamllow schema

Version v6.10.1 (released 2024-12-12)

- names: drop unique id on the internal id

Version v6.10.0 (released 2024-12-12)

- names: add internal id column to the name_metadata db

Version v6.9.0 (released 2024-12-09)

- schema: added identifiers in affiliations relation

Version v6.8.0 (released 2024-12-09)

- names: extract affiliation identifiers from employments
- names: optimize memory usage on ORCID sync
- subjects: improve search with CompositeSuggestQueryParser
- subjects: added datastream for bodc

Version v6.7.0 (released 2024-11-27)

- contrib: improve search accuracy for names, funders, affiliations
- names: add affiliation acronym in mappings and schema
    * Dereferences the affiliation `acronym` when indexing names and serving
      REST API results. This is useful for disambiguating authors in search.
- affiliations: move RDF and SPARQL as extra dependencies
    * Moves `rdflib` and `SPARQLWrapper` to extras.
- affiliation: refactored edmo datastreams
- subjects: added datastream for GEMET vocabulary
- awards/schema.py: read app config for alternate funding validation (#429)
- awards: fix description field and mappings
- awards: add fields start/end date and description

Version v6.6.0 (released 2024-11-15)

- mesh: add title en if not present
- subjects: add subject to search fields
- jobs: add ORCID job
- global: Add unlisted tag
    * This adds a new tag to the vocabularies to allow for unlisted
      vocabularies. This is useful for vocabularies that are not meant to be
      displayed in the UI.
    * This requires to update the names mapping to add the props.

Version v6.5.0 (released 2024-10-31)

- subjects: euroscivoc: change default to latest version-less URL
- Rename patched filters so the normalizer uses the default ones (#409)
    * rename patched filters so the normalizer uses the default ones

Version v6.4.1 (released 2024-10-15)

- fix: exclude unknown fields when updating awards with subjects
- fix: revert generic writer and define OpenAIRE awards writer logic

Version v6.4.0 (released 2024-10-15)

- jobs: add import awards OpenAIRE; Update CORDIS
- awards: rollback to use the 2nd part of funding stream as program

Version v6.3.1 (released 2024-10-11)

- jobs: pass since as string to task

Version v6.3.0 (released 2024-10-11)

- awards: get program from CORDIS
- fix: add 'en' title if missing ROR
- fix: since not passed to args
- jobs: add process funders job

Version v6.2.1 (released 2024-10-10)

- webpack: bump react-searchkit due to axios upgrade

Version v6.2.0 (released 2024-10-10)

- tests: update axios version (needed only for local js tests)

Version v6.1.0 (released 2024-10-10)

- jobs: define invenio job wrapper for ROR affiliation data stream
- awards: remove subj props from jsonschema

Version v6.0.0 (released 2024-10-03)

- datastreams: writers: add option to not insert
- subjects: added euroscivoc datastream
- affiliations: OpenAIRE transformer and writer adding PIC identifier
- awards: added subjects and participating organizations from CORDIS datastreams
- names: add permission check to names search

Version v5.1.0 (released 2024-09-25)

- funders: tune search boost for acronyms
    * Add and `acronym.keyword` field to the funders mapping.
    * Apply to funders the same field boosting as in affiliations.

Version v5.0.3 (released 2024-09-06)

- services: skip index rebuilding

Version v5.0.2 (released 2024-08-28)

- ror: use datePublished as fallback date for dataset timestamp

Version v5.0.1 (released 2024-08-27)

- mapping: fix normalizer

Version v5.0.0 (released 2024-08-22)

- affiliations: dd analyzers and filters to improve results when searching affiliations

Version v4.4.0 (released 2024-08-09)

- services: use and adjust vnd.inveniordm.v1+json http accept header

Version v4.3.0 (released 2024-08-05)

- names: make names_exclude_regex configurable
- names: validate entry full names
- names: add orcid public data sync

Version v4.2.0 (released 2024-07-24)

- ror: check last update; use ld+json for metadata (#367)
- tasks: remove import funders task
- funders: add and export custom transformer
- affiliations: add and export custom transformer
- datastreams: implement asynchronous writer

Version v4.1.1 (released 2024-07-15)

- installation: use invenio-oaipmh-scythe from PyPI

Version v4.1.0 (released 2024-07-15)

- readers: make OAI-PMH an optional extra
- schema: add administration UI attributes
- ror: fix duplicate acronymns and aliases
- affiliations: fix title search
- datastreams: have yaml writer output utf8
- datastreams: add configs for funders and affiliations
- affiliations: add datastreams
- datastreams: move ror transformer to common
- vocabulary-types: services, resources, and administration UI (#310)
- config: add OpenAIRE mapping for "Latvian Council of Science"
- funders: fix country name display (#343)
- Initial implementation of OAIPMHReader (#329)
- global: add "tags" field to all vocabularies

Version 4.0.0 (released 2024-06-04)

- datastreams: implement factories for generating vocabulary configurations
- datastreams: added ROR HTTP reader
- funders: use ROR v2 dump instead of v1
- datastreams: added celery task for funders using ROR HTTP reader
- datastreams: add OpenAIRE Project HTTP Reader
- datastreams: fix OpenAIRE graph dataset parsing
- installation: upgrade invenio-records-resources

Version 3.4.0 (released 2024-04-19)

- templates: add subject fields UI template (#303)

Version 3.3.0 (released 2024-04-16)

- assets: add overridable awards and funding

Version 3.2.0 (released 2024-03-22)

- funding: add country and ror to funder search results
- init: move record_once to finalize_app (removes deprecation on `before_first_request`)
- installation: upgrade invenio-app


Version 3.1.0 (released 2024-03-05)

- custom_fields: added subject field
- custom_fields: add pid_field to custom fields
- mappings: change "dynamic" values to string
- ci: upgrade tests matrix
- bumps react-invenio-forms

Version 3.0.0 (released 2024-01-30)

- installation: bump invenio-records-resources

Version 2.4.0 (2023-12-07)

- schema: add validation for affiliations
- mappings: add a text subfield for award acronyms
- config: add new TWCF funder

Version 2.3.1 (2023-11-01)

- contrib: add affiliation suggestion by id

Version 2.3.0 (2023-10-25)

- contrib: allow search funders by id
- contrib: funders and awards fix TransportError in OS caused by suggestion search in too many fields

Version 2.2.4 (2023-10-19)

- search: decrease number of searching fields

Version 2.2.3 (2023-10-08)

- contrib: fix ``name`` serialization for the Names vocabulary.

Version 2.2.2 (2023-10-06)

- alembic rcp: set explicit dependency on pidstore create table

Version 2.2.1 (2023-10-02)

- facets: change caching strategy by caching each vocabulary by id. Replace
  lru_cache with invenio-cache to ensure that cache expiration uses a TTL that
  is correctly computed.

Version 2.2.0 (2023-09-19)

- facets: implement in-memory cache

Version 2.1.1 (2023-09-19)

- funding: fixed accessiblity issues

Version 2.1.0 (2023-09-15)

- custom_fields: allow to pass schema to the VocabularyCF
- affiliations: add facet labels

Version 2.0.0 (2023-09-14)

- contrib-awards: add "program" to schema fields
- global: switch names and affiliations to model PID field
- ci: update matrix
- awards: add "program" field
- config: update awards funders mapping
- service: add sort option to load vocabs

Version 1.6.0 (2023-09-12)

- awards: add acronym to schema

Version 1.5.1 (2023-07-07)

- fix string type columns for mysql

Version 1.5.0 (2023-04-25)

- upgrade invenio-records-resources

Version 1.4.0 (2023-04-20)

- upgrade invenio-records-resources

Version 1.3.0 (2023-04-20)

- add UI deposit contrib components

Version 1.2.0 (2023-03-24)

- bump invenio-records-resources to v2.0.0

Version 1.1.0 (released 2023-03-02)

- serializers: deprecate marshamllow JSON
- mappings: add dynamic template for i18n titles and descriptions
- remove deprecated flask-babelex dependency and imports

Version 1.0.4 (released 2023-01-20)

- funders: Add ROR to identifiers for all funders in datastream
- facets: add not found facet exception (when facet is configured but not provided in setup)
- facets: handle non existing vocabulary type

Version 1.0.3 (released 2022-11-25)

- Add i18n translations.

Version 1.0.2 (released 2022-11-14)

- Fix missing field_args in VocabularyCF

Version 1.0.1 (released 2022-11-14)

- Allow kwargs in VocabularyCF

Version 1.0.0 (released 2022-11-04)

- Bump invenio-records-resources

Version 0.1.5 (released 2020-12-11)

- Bug fixes in contrib vocabulary

Version 0.1.4 (released 2020-12-11)

- Add subjects vocabulary

Version 0.1.3 (released 2020-12-11)

- Include csv vocabularies data

Version 0.1.2 (released 2020-12-11)

- CI changes

Version 0.1.1 (released 2020-12-11)

- Add vocabulary import command

Version 0.1.0 (released 2020-12-08)

- Initial public release.
