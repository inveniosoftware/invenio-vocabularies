import pytest
from marshmallow.exceptions import \
    ValidationError as MarshmallowValidationError
from sqlalchemy.exc import IntegrityError

from invenio_vocabularies.records.models import VocabularyType


def test_record_validation(app, db, identity, service, example_record):
    """Test vocabulary item validation."""
    vocabulary_type = VocabularyType(name="test")
    db.session.add(vocabulary_type)
    db.session.commit()

    def create(metadata):
        return service.create(
            identity=identity,
            data=dict(
                metadata=metadata, vocabulary_type_id=vocabulary_type.id
            ),
        )

    def check_invalid(metadata):
        with pytest.raises(MarshmallowValidationError):
            create(metadata)

    # valid items
    create({})
    create({"title": {}})
    assert create({"nonexistent": "value"}).data["metadata"] == {}

    # invalid items
    check_invalid({"title": "Title"})
    check_invalid({"title": {"not a language": "Title"}})
    check_invalid({"props": {"key": {}}})

    # missing foreign key
    with pytest.raises(IntegrityError):
        service.create(
            identity=identity, data=dict(metadata={}, vocabulary_type_id=-1)
        )
    db.session.rollback()

    # invalid update
    with pytest.raises(MarshmallowValidationError):
        service.update(
            example_record.id, identity, dict(metadata={"description": 1})
        )

    # valid update
    service.update(
        example_record.id,
        identity,
        dict(metadata={"title": {"en": "Other title"}}),
    )


def test_record_item_pid(app, db, identity, service):
    record_item = service.create(
        identity=identity,
        data={"metadata": {"title": {"en": "ABC"}, "vocabulary_type_id": 1}},
    )
    assert record_item.id
    assert record_item._record.pid.status == "R"
