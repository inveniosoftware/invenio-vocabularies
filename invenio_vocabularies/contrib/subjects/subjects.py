from invenio_records_resources.factories.factory import RecordTypeFactory

from invenio_vocabularies.contrib.subjects.permissions import PermissionPolicy
from invenio_vocabularies.contrib.subjects.schema import SubjectSchema

subject_record_type = RecordTypeFactory(
    "Subject", SubjectSchema,
    permission_policy_cls=PermissionPolicy
)
