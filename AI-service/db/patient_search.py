from typing import Optional

import jellyfish

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

NAME_WEIGHT = 0.6
AGE_WEIGHT = 0.25
SEX_WEIGHT = 0.15

AGE_TOLERANCE = 3

STRONG_THRESHOLD = 0.85

MATCH_STRONG = "strong"
MATCH_ASK = "ask"


def name_similarity(query_value: Optional[str], candidate_value: Optional[str]) -> float:
    if not query_value or not candidate_value:
        return 0.0
    return jellyfish.jaro_winkler_similarity(query_value.lower(), candidate_value.lower())


def age_agreement(query_value: Optional[int], candidate_value: Optional[int]) -> float:

    if query_value is None or candidate_value is None:
        return 0.0
    return 1.0 if abs(query_value - candidate_value) <= AGE_TOLERANCE else 0.0


def exact_match(query_value: Optional[str], candidate_value: Optional[str]) -> float:
    if not query_value or not candidate_value:
        return 0.0
    return 1.0 if query_value.lower() == candidate_value.lower() else 0.0


FIELD_MATCHERS = [
    ("name", NAME_WEIGHT, name_similarity),
    ("age", AGE_WEIGHT, age_agreement),
    ("sex", SEX_WEIGHT, exact_match),
]


def _participating_matchers(query: dict) -> list[tuple[str, float, callable]]:
    """Matchers whose query value is present.

    A field missing from the query (age/sex not given) is neutral — it's
    excluded from the weighted average rather than scored as a mismatch, so
    it doesn't drag the score down. Name always participates; it's the
    primary key of a patient lookup.
    """
    return [
        (field, weight, comparator)
        for field, weight, comparator in FIELD_MATCHERS
        if query.get(field) is not None
    ]


def score_candidate(query: dict, candidate: dict) -> float:
    """Bounded 0..1 weighted-average match score for one candidate.

    `query`/`candidate` are dicts with name/age/sex keys. Only matchers whose
    query value is present participate (see `_participating_matchers`).
    """
    matchers = _participating_matchers(query)
    total_weight = sum(weight for _, weight, _ in matchers)
    if total_weight == 0:
        return 0.0
    weighted_sum = sum(
        weight * comparator(query.get(field), candidate.get(field))
        for field, weight, comparator in matchers
    )
    return weighted_sum / total_weight


def match_breakdown(query: dict, candidate: dict) -> dict:
    """Per-field subscores behind `score_candidate`, for explainability/logging.

    e.g. {"name": 0.62} lets a caller say "asked because name=0.62".
    """
    return {
        field: comparator(query.get(field), candidate.get(field))
        for field, _weight, comparator in _participating_matchers(query)
    }


def classify_match(score: float) -> str:
    """MATCH_STRONG (auto-link) if score >= STRONG_THRESHOLD, else MATCH_ASK."""
    return MATCH_STRONG if score >= STRONG_THRESHOLD else MATCH_ASK


def build_patient_query(
    doctor_id: str,
    name: Optional[str] = None,
    age: Optional[int] = None,
    sex: Optional[str] = None,
) -> dict:
    """Build the fuzzy-name + soft-boost OpenSearch query, all filters optional.

    doctorId is always a hard filter. name (if given) is a fuzzy `must` match;
    age/sex (if given) are `should` boosts, not filters, so a near-miss on age
    or sex doesn't exclude an otherwise good name match. Shared by the
    save-flow candidate search (`search_patients`) and the read-only
    `query_patients` tool.
    """
    should = []
    must = []

    if sex:
        should.append({"term": {OPENSEARCH_FIELD_SEX: {"value": sex, "boost": SEX_MATCH_BOOST}}})

    if age is not None:
        should.append(
            {
                "range": {
                    OPENSEARCH_FIELD_AGE: {
                        "gte": age - AGE_MATCH_RANGE_YEARS,
                        "lte": age + AGE_MATCH_RANGE_YEARS,
                        "boost": AGE_MATCH_BOOST,
                    }
                }
            }
        )

    if name:
        must.append({"match": {OPENSEARCH_FIELD_NAME: {"query": name, "fuzziness": "AUTO"}}})

    return {
        "bool": {
            "filter": [{"term": {OPENSEARCH_FIELD_DOCTOR_ID: doctor_id}}],
            "must": must,
            "should": should,
        }
    }

def patients_from_hits(
    hits: list[dict],
    name: Optional[str] = None,
    age: Optional[int] = None,
    sex: Optional[str] = None,
) -> list[dict]:
    """Turn raw OpenSearch hits into scored, ranked candidates.

    name/age/sex are the doctor's query values (not OpenSearch's `_score`,
    which is unbounded and unsuitable for thresholding — see the module
    docstring above `score_candidate`). Results are re-sorted descending by
    `match_score` rather than kept in OpenSearch's relevance order, since our
    bounded score is the actual confidence signal callers act on.
    """
    query = {"name": name, "age": age, "sex": sex}

    candidates = [
        {
            "patient": PatientSummary(
                id=hit["_source"].get(OPENSEARCH_FIELD_ID),
                name=hit["_source"].get(OPENSEARCH_FIELD_NAME),
                age=hit["_source"].get(OPENSEARCH_FIELD_AGE),
                sex=hit["_source"].get(OPENSEARCH_FIELD_SEX),
            ),
        }
        for hit in hits
    ]

    for candidate in candidates:
        patient = candidate["patient"]
        candidate_fields = {"name": patient.name, "age": patient.age, "sex": patient.sex}
        candidate["match_score"] = score_candidate(query, candidate_fields)
        candidate["match_breakdown"] = match_breakdown(query, candidate_fields)

    candidates.sort(key=lambda c: c["match_score"], reverse=True)
    return candidates


def search_patients(doctor_id: str, patient: Patient) -> list[dict]:
    response = client.search(
        index=OPENSEARCH_PATIENTS_INDEX,
        body={
            "size": MAX_CANDIDATES,
            "query": build_patient_query(
                doctor_id, name=patient.name, age=patient.age, sex=patient.sex
            ),
        },
    )

    hits = response["hits"]["hits"]
    if not hits:
        return []

    return patients_from_hits(hits, name=patient.name, age=patient.age, sex=patient.sex)
