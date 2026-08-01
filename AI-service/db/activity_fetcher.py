from datetime import datetime
from typing import Optional

from graph.models.activity import Activity

from .connection import driver


def find_activities(
    doctor_id: str,
    activity_type: Optional[str],
    lower: Optional[datetime],
    upper: Optional[datetime],
) -> list[Activity]:
    conditions = []
    params = {"doctor_id": doctor_id}

    if lower is not None:
        conditions.append("a.start >= $lower")
        params["lower"] = lower.isoformat()

    if upper is not None:
        conditions.append("a.start < $upper")
        params["upper"] = upper.isoformat()

    if activity_type is not None:
        conditions.append("a.name = $activity_type")
        params["activity_type"] = activity_type

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"""
    MATCH (d:Doctor {{id: $doctor_id}})-[:LOGGED]->(a:Activity)
    {where_clause}
    RETURN a
    ORDER BY a.start
    """

    def _read(tx):
        return [record["a"] for record in tx.run(query, **params)]

    with driver.session() as session:
        nodes = session.execute_read(_read)

    return [_to_activity(node) for node in nodes]


def _to_activity(node) -> Activity:
    return Activity(
        id=node.get("id"),
        name=node.get("name"),
        start=datetime.fromisoformat(node["start"]) if node.get("start") else None,
        end=datetime.fromisoformat(node["end"]) if node.get("end") else None,
        location=node.get("location"),
        notes=node.get("notes"),
    )
