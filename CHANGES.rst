..
    Copyright (C) 2020-2024 CERN.

    Invenio-Vocabularies is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======

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
