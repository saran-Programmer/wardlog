import json
from typing import Optional

from .opensearch_connection import client
from .opensearch_constants import OPENSEARCH_PATIENTS_INDEX
from .patient_search import MAX_CANDIDATES, build_patient_query, patients_from_hits


def query_patients(
    doctor_id: str,
    name: Optional[str] = None,
    age: Optional[int] = None,
    sex: Optional[str] = None,
) -> list[dict]:
    """Query this doctor's Patient records in OpenSearch, all filters optional.

    Read-only. `doctor_id` scopes the query and is always injected by code,
    never taken from LLM input. name/age/sex are passed straight to
    `build_patient_query` — the same fuzzy-name + soft-boost query used by the
    save-flow candidate search in `patient_search.search_patients` — so the
    two callers stay in sync rather than drifting apart.

    Returns the same shape as `search_patients`: a list of
    {"patient": PatientSummary, "match_score": float, "match_breakdown": dict}.
    """
    query = build_patient_query(doctor_id, name=name, age=age, sex=sex)
    body = {"size": MAX_CANDIDATES, "query": query}

    print("\n" + "=" * 100)
    print("QUERY_PATIENTS: outgoing request")
    print("=" * 100)
    print(f"doctor_id={doctor_id!r} name={name!r} age={age!r} sex={sex!r}")
    print("-" * 100)
    print(f"OpenSearch query body: {json.dumps(body, indent=2, default=str)}")
    print("=" * 100 + "\n")

    response = client.search(index=OPENSEARCH_PATIENTS_INDEX, body=body)
    hits = response["hits"]["hits"]

    print("\n" + "#" * 100)
    print("QUERY_PATIENTS: raw hits returned by OpenSearch")
    print("#" * 100)
    if not hits:
        print("(no hits returned)")
    for i, hit in enumerate(hits):
        print(f"--- hit {i} --- score={hit['_score']!r} source={hit['_source']!r}")
    print("#" * 100 + "\n")

    if not hits:
        return []

    results = patients_from_hits(hits, name=name, age=age, sex=sex)

    print("\n" + "*" * 100)
    print("QUERY_PATIENTS: final result list returned to caller")
    print("*" * 100)
    print(
        json.dumps(
            [
                {
                    "patient": r["patient"].model_dump(mode="json"),
                    "match_score": r["match_score"],
                    "match_breakdown": r["match_breakdown"],
                }
                for r in results
            ],
            indent=2,
            default=str,
        )
    )
    print("*" * 100 + "\n")

    return results
