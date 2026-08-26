from typing import Any

from graph.models.activity import Activity

from .activity_fetcher import _to_activity
from .connection import driver

# Fields the tool is allowed to filter on, and the operators valid for each
# field's type. Extend this map (and _OPERATOR_TEMPLATES) to add more
# filterable fields/entities later, e.g. Patient.
_ALLOWED_FILTERS: dict[str, dict[str, Any]] = {
    "name": {"type": "enum", "operators": {"eq", "neq", "in"}},
    "start": {"type": "datetime", "operators": {"eq", "before", "after", "between"}},
    "end": {"type": "datetime", "operators": {"eq", "before", "after", "between"}},
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


def query_activities(doctor_id: str, filters: list[dict]) -> list[Activity]:
    """Query this doctor's Activity nodes, AND-ing together `filters`.

    Read-only. `doctor_id` scopes the query and is always injected by code,
    never taken from `filters`. Each filter is validated against
    `_ALLOWED_FILTERS` before being turned into a parameterized Cypher
    condition; an invalid filter raises ValueError.

    start/end are stored as ISO 8601 strings, which compare correctly under
    plain lexicographic (string) ordering, so string comparison in Cypher is
    sufficient — no datetime parsing is needed on the Cypher side.
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

    query = f"""
    MATCH (a:Activity)
    WHERE {' AND '.join(conditions)}
    RETURN a
    ORDER BY a.start
    """

    def _read(tx):
        return [record["a"] for record in tx.run(query, **params)]

    with driver.session() as session:
        nodes = session.execute_read(_read)

    return [_to_activity(node) for node in nodes]
