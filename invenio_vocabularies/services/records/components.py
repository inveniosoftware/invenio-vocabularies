from invenio_records_resources.services.records.components import \
    ServiceComponent


class VocabularyTypeComponent(ServiceComponent):
    """Service component for metadata."""

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject vocabulary type to the record."""
        record.vocabulary_type_id = data.get('vocabulary_type_id', None)

    def update(self, identity, data=None, record=None, **kwargs):
        """Inject vocabulary type to the record."""
        record.vocabulary_type_id = data.get('vocabulary_type_id', None)

