import os

from opensearchpy import OpenSearch

from .opensearch_constants import (
    OPENSEARCH_FIELD_AGE,
    OPENSEARCH_FIELD_DOCTOR_ID,
    OPENSEARCH_FIELD_ID,
    OPENSEARCH_FIELD_NAME,
    OPENSEARCH_FIELD_PATIENT_REFERENCE_ID,
    OPENSEARCH_FIELD_SEX,
    OPENSEARCH_PATIENTS_INDEX,
)

_username = os.environ.get("OPENSEARCH_USERNAME")
_password = os.environ.get("OPENSEARCH_PASSWORD")

client = OpenSearch(
    hosts=[
        {
            "host": os.environ["OPENSEARCH_HOST"],
            "port": int(os.environ["OPENSEARCH_PORT"]),
        }
    ],
    http_auth=(_username, _password) if _username and _password else None,
    use_ssl=os.environ.get("OPENSEARCH_USE_SSL", "false").lower() == "true",
    verify_certs=os.environ.get("OPENSEARCH_VERIFY_CERTS", "false").lower() == "true",
)

PATIENTS_INDEX_MAPPING = {
    "mappings": {
        "properties": {
            OPENSEARCH_FIELD_NAME: {"type": "text"},
            OPENSEARCH_FIELD_ID: {"type": "keyword"},
            OPENSEARCH_FIELD_DOCTOR_ID: {"type": "keyword"},
            OPENSEARCH_FIELD_SEX: {"type": "keyword"},
            OPENSEARCH_FIELD_PATIENT_REFERENCE_ID: {"type": "keyword"},
            OPENSEARCH_FIELD_AGE: {"type": "integer"},
        }
    }
}


def verify_connection() -> None:
    client.info()


def ensure_patients_index() -> None:
    if not client.indices.exists(index=OPENSEARCH_PATIENTS_INDEX):
        client.indices.create(index=OPENSEARCH_PATIENTS_INDEX, body=PATIENTS_INDEX_MAPPING)
