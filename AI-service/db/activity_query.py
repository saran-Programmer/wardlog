import json
from typing import Any, Optional

from graph.models.activity_query_result import ActivityResult, ConsultationResult, PatientResult

from .activity_fetcher import _to_activity
from .connection import driver

_ALLOWED_FILTERS: dict[str, dict[str, Any]] = {
    "name": {"type": "enum", "operators": {"eq", "neq", "in"}},
    "start": {"type": "datetime", "operators": {"eq", "before", "after", "between"}},
    "end": {"type": "datetime", "operators": {"eq", "before", "after", "between"}},
}

_ALLOWED_INCLUDES: set[str] = {
    "consultations",
    "patients",
    "diagnoses",
    "drugs",
    "surgery_type",
}

_OPERATOR_TEMPLATES = {
    "eq": "a.{field} = $p{i}",
    "neq": "a.{field} <> $p{i}",
    "in": "a.{field} IN $p{i}",
    "before": "a.{field} < $p{i}",
    "after": "a.{field} > $p{i}",
    "between": "a.{field} >= $p{i}_from AND a.{field} <= $p{i}_to",
}


def _validate_filter(field: Any, operator: Any, value: Any) -> None:
    spec = _ALLOWED_FILTERS.get(field)
    if spec is None:
        raise ValueError(f"Unknown or disallowed filter field: {field!r}")

    if operator not in spec["operators"]:
        raise ValueError(f"Operator {operator!r} is not valid for field {field!r}")

    if operator == "in":
        if not isinstance(value, list) or not value or not all(isinstance(v, str) for v in value):
            raise ValueError(f"Operator 'in' requires a non-empty list of strings, got {value!r}")
    elif operator == "between":
        if (
            not isinstance(value, list)
            or len(value) != 2
            or not all(isinstance(v, str) for v in value)
        ):
            raise ValueError(f"Operator 'between' requires a 2-item list [from, to], got {value!r}")
    else:
        if not isinstance(value, str):
            raise ValueError(f"Operator {operator!r} requires a string value, got {value!r}")


def _build_condition(index: int, field: str, operator: str, value: Any) -> tuple[str, dict[str, Any]]:
    condition = _OPERATOR_TEMPLATES[operator].format(field=field, i=index)

    if operator == "between":
        params = {f"p{index}_from": value[0], f"p{index}_to": value[1]}
    else:
        params = {f"p{index}": value}

    return condition, params


def _validate_include(include: Optional[list[str]]) -> set[str]:
    if not include:
        return set()

    invalid = set(include) - _ALLOWED_INCLUDES
    if invalid:
        raise ValueError(
            f"Unknown or disallowed include value(s): {sorted(invalid)!r}. "
            f"Allowed values: {sorted(_ALLOWED_INCLUDES)!r}"
        )

    return set(include)


def _debug_render_query(query: str, params: dict[str, Any]) -> str:
    """Substitute `params` into `query` text for debug printing only.

    Longer keys are substituted first so e.g. $p0_from isn't corrupted by a
    prior replacement of $p0. The real query passed to the driver stays
    parameterized — this is display-only, never executed.
    """
    rendered = query
    for key in sorted(params, key=len, reverse=True):
        rendered = rendered.replace(f"${key}", repr(params[key]))
    return rendered


def _to_activity_result(activity_node: Any, consultations: list[dict]) -> ActivityResult:
    return ActivityResult(
        activity=_to_activity(activity_node),
        consultations=[
            ConsultationResult(
                id=c["id"],
                patient=(
                    PatientResult(
                        id=c["patient_id"],
                        name=c["patient_name"],
                        age=c["patient_age"],
                        sex=c["patient_sex"],
                    )
                    if c["patient_name"] is not None
                    else None
                ),
                diagnoses=c["diagnoses"],
                drugs=c["drugs"],
                surgery_type=c["surgery_type"],
            )
            for c in consultations
        ],
    )


def query_activities(
    doctor_id: str, filters: list[dict], include: Optional[list[str]] = None
) -> list[ActivityResult]:
    """Query this doctor's Activity nodes, AND-ing together `filters`.

    Read-only. `doctor_id` scopes the query and is always injected by code,
    never taken from `filters`. Each filter is validated against
    `_ALLOWED_FILTERS` before being turned into a parameterized Cypher
    condition; an invalid filter raises ValueError.

    start/end are stored as ISO 8601 strings, which compare correctly under
    plain lexicographic (string) ordering, so string comparison in Cypher is
    sufficient — no datetime parsing is needed on the Cypher side.

    `include` optionally names related data to fetch alongside each activity,
    validated against `_ALLOWED_INCLUDES`. Activities always come back;
    `ActivityResult.consultations` is empty unless `include` asks for it (or
    for something that hangs off it).
    """
    conditions = ["a.doctorId = $doctor_id"]
    params: dict[str, Any] = {"doctor_id": doctor_id}

    for index, f in enumerate(filters):
        field = f.get("field")
        operator = f.get("operator")
        value = f.get("value")

        _validate_filter(field, operator, value)

        condition, condition_params = _build_condition(index, field, operator, value)
        conditions.append(condition)
        params.update(condition_params)

    included = _validate_include(include)

    if not included:
        query = f"""
        MATCH (a:Activity)
        WHERE {' AND '.join(conditions)}
        RETURN a
        ORDER BY a.start
        """

        def _read(tx):
            return [(record["a"], []) for record in tx.run(query, **params)]

    else:
        want_patient = "patients" in included
        want_diagnoses = "diagnoses" in included
        want_drugs = "drugs" in included
        want_surgery_type = "surgery_type" in included

        patient_match = (
            "OPTIONAL MATCH (c)-[:WITH_PATIENT]->(p:Patient {doctorId: $doctor_id})"
            if want_patient else ""
        )
        diagnosis_match = (
            "OPTIONAL MATCH (c)-[:HAS_DIAGNOSIS]->(dx:Diagnosis {doctorId: $doctor_id})"
            if want_diagnoses else ""
        )
        drug_match = (
            "OPTIONAL MATCH (c)-[:PRESCRIBED]->(dr:Drug {doctorId: $doctor_id})"
            if want_drugs else ""
        )
        surgery_type_match = (
            "OPTIONAL MATCH (c)-[:SURGERY_TYPE]->(st:SurgeryType {doctorId: $doctor_id})"
            if want_surgery_type else ""
        )

        patient_id_expr = "p.id" if want_patient else "null"
        patient_name_expr = "p.name" if want_patient else "null"
        patient_age_expr = "p.age" if want_patient else "null"
        patient_sex_expr = "p.sex" if want_patient else "null"
        diagnoses_expr = "collect(DISTINCT dx.name)" if want_diagnoses else "[]"
        drugs_expr = "collect(DISTINCT dr.name)" if want_drugs else "[]"
        surgery_type_expr = "st.name" if want_surgery_type else "null"

        query = f"""
        MATCH (a:Activity)
        WHERE {' AND '.join(conditions)}
        WITH a
        OPTIONAL MATCH (a)-[:HAS_CONSULTATION]->(c:Consultation {{doctorId: $doctor_id}})
        {patient_match}
        {diagnosis_match}
        {drug_match}
        {surgery_type_match}
        WITH a, c,
             {patient_id_expr} AS patient_id,
             {patient_name_expr} AS patient_name,
             {patient_age_expr} AS patient_age,
             {patient_sex_expr} AS patient_sex,
             {diagnoses_expr} AS diagnoses,
             {drugs_expr} AS drugs,
             {surgery_type_expr} AS surgery_type
        WITH a, [x IN collect(CASE WHEN c IS NULL THEN NULL ELSE {{
            id: c.id,
            patient_id: patient_id,
            patient_name: patient_name,
            patient_age: patient_age,
            patient_sex: patient_sex,
            diagnoses: diagnoses,
            drugs: drugs,
            surgery_type: surgery_type
        }} END) WHERE x IS NOT NULL] AS consultations
        RETURN a, consultations
        ORDER BY a.start
        """
        
        def _read(tx):
            return [
                (record["a"], record["consultations"])
                for record in tx.run(query, **params)
            ]

    print("\n" + "=" * 100)
    print("QUERY_ACTIVITIES: outgoing request")
    print("=" * 100)
    print(f"doctor_id={doctor_id!r} filters={filters!r} include={include!r}")
    print("-" * 100)
    print("CYPHER (params resolved inline for readability; actual call stays parameterized):")
    print(_debug_render_query(query, params))
    print("-" * 100)
    print(f"raw params dict: {params!r}")
    print("=" * 100 + "\n")

    with driver.session() as session:
        rows = session.execute_read(_read)

    print("\n" + "#" * 100)
    print("QUERY_ACTIVITIES: raw rows returned by Neo4j")
    print("#" * 100)
    if not rows:
        print("(no rows returned)")
    for i, (node, consultations) in enumerate(rows):
        print(f"--- row {i} ---")
        print(f"activity node properties: {dict(node)!r}")
        print(f"consultations: {consultations!r}")
    print("#" * 100 + "\n")

    results = [_to_activity_result(node, consultations) for node, consultations in rows]

    print("\n" + "*" * 100)
    print("QUERY_ACTIVITIES: final ActivityResult list returned to caller")
    print("*" * 100)
    print(json.dumps([r.model_dump(mode="json") for r in results], indent=2, default=str))
    print("*" * 100 + "\n")

    return results
