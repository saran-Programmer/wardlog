from graph.models.consultation import Patient
from graph.models.patient_details import PatientSummary

from .opensearch_connection import client
from .opensearch_constants import (
    OPENSEARCH_FIELD_AGE,
    OPENSEARCH_FIELD_DOCTOR_ID,
    OPENSEARCH_FIELD_ID,
    OPENSEARCH_FIELD_NAME,
    OPENSEARCH_FIELD_SEX,
    OPENSEARCH_PATIENTS_INDEX,
)

MAX_CANDIDATES = 7

SEX_MATCH_BOOST = 1.0
AGE_MATCH_BOOST = 1.0
AGE_MATCH_RANGE_YEARS = 3


def _build_query(doctor_id: str, patient: Patient) -> dict:
    should = []

    if patient.sex:
        should.append(
            {"term": {OPENSEARCH_FIELD_SEX: {"value": patient.sex, "boost": SEX_MATCH_BOOST}}}
        )

    if patient.age is not None:
        should.append(
            {
                "range": {
                    OPENSEARCH_FIELD_AGE: {
                        "gte": patient.age - AGE_MATCH_RANGE_YEARS,
                        "lte": patient.age + AGE_MATCH_RANGE_YEARS,
                        "boost": AGE_MATCH_BOOST,
                    }
                }
            }
        )

    return {
        "bool": {
            "filter": [{"term": {OPENSEARCH_FIELD_DOCTOR_ID: doctor_id}}],
            "must": [
                {"match": {OPENSEARCH_FIELD_NAME: {"query": patient.name, "fuzziness": "AUTO"}}}
            ],
            "should": should,
        }
    }


def _match_percentage(score: float, max_score: float) -> int:
    # Relative to the top hit in this result set, not an absolute confidence
    # value — a 100 here just means "best match among these candidates".
    if not max_score:
        return 0
    return round((score / max_score) * 100)


def search_patients(doctor_id: str, patient: Patient) -> list[dict]:
    response = client.search(
        index=OPENSEARCH_PATIENTS_INDEX,
        body={"size": MAX_CANDIDATES, "query": _build_query(doctor_id, patient)},
    )

    hits = response["hits"]["hits"]
    if not hits:
        return []

    max_score = response["hits"]["max_score"]

    return [
        {
            "patient": PatientSummary(
                id=hit["_source"].get(OPENSEARCH_FIELD_ID),
                name=hit["_source"].get(OPENSEARCH_FIELD_NAME),
                age=hit["_source"].get(OPENSEARCH_FIELD_AGE),
                sex=hit["_source"].get(OPENSEARCH_FIELD_SEX),
            ),
            "match_percentage": _match_percentage(hit["_score"], max_score),
        }
        for hit in hits 
    ]
