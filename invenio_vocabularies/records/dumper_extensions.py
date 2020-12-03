from invenio_records.dumpers import ElasticsearchDumperExt

from invenio_vocabularies.records.models import VocabularyType


class VocabularyTypeElasticsearchDumperExt(ElasticsearchDumperExt):

    def dump(self, record, data):
        vocabulary_type_id = data.get('vocabulary_type_id')
        if vocabulary_type_id:
            data["vocabulary_type"] =\
                VocabularyType.query.get(vocabulary_type_id).name
            data["vocabulary_type_id"] = \
                VocabularyType.query.get(vocabulary_type_id).id
        super().dump(record, data)

    def load(self, data, record_cls):
        vocabulary_type_id = data.get('vocabulary_type_id')
        if vocabulary_type_id:
            data["vocabulary_type"] = \
                VocabularyType.query.get(vocabulary_type_id).name
            data["vocabulary_type_id"] = \
                VocabularyType.query.get(vocabulary_type_id).id
        super().load(data, record_cls)

