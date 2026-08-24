from graph.models.consultation import Patient

from .opensearch_connection import client
from .opensearch_constants import (
    OPENSEARCH_FIELD_AGE,
    OPENSEARCH_FIELD_DOCTOR_ID,
    OPENSEARCH_FIELD_ID,
    OPENSEARCH_FIELD_NAME,
    OPENSEARCH_FIELD_PATIENT_REFERENCE_ID,
    OPENSEARCH_FIELD_SEX,
    OPENSEARCH_PATIENTS_INDEX,
)


def index_patient(patient_id: str, doctor_id: str, patient: Patient) -> None:
    body = {
        OPENSEARCH_FIELD_ID: patient_id,
        OPENSEARCH_FIELD_DOCTOR_ID: doctor_id,
        OPENSEARCH_FIELD_NAME: patient.name,
        OPENSEARCH_FIELD_AGE: patient.age,
        OPENSEARCH_FIELD_SEX: patient.sex,
        OPENSEARCH_FIELD_PATIENT_REFERENCE_ID: patient.patient_reference_id,
    }

    client.index(index=OPENSEARCH_PATIENTS_INDEX, id=patient_id, body=body)
