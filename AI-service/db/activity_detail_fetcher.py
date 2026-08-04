from typing import Optional

from graph.models.activity_details import ActivityDetails

from .connection import driver

_ACTIVITY_QUERY = "MATCH (a:Activity {id: $activity_id}) RETURN a"

_CONSULTATIONS_QUERY = """
MATCH (a:Activity {id: $activity_id})-[:HAS_CONSULTATION]->(c:Consultation)
OPTIONAL MATCH (c)-[:WITH_PATIENT]->(p:Patient)
OPTIONAL MATCH (c)-[:HAS_DIAGNOSIS]->(dx:Diagnosis)
OPTIONAL MATCH (c)-[:PRESCRIBED]->(dr:Drug)
OPTIONAL MATCH (c)-[:SURGERY_TYPE]->(st:SurgeryType)
RETURN p.name AS patient_name,
       p.age AS patient_age,
       p.sex AS patient_sex,
       collect(DISTINCT dx.name) AS diagnoses,
       collect(DISTINCT dr.name) AS drugs,
       st.name AS surgery_type
"""


def find_activity_details(activity_id: str) -> Optional[ActivityDetails]:
    def _read(tx):
        activity_record = tx.run(_ACTIVITY_QUERY, activity_id=activity_id).single()
        if activity_record is None:
            return None

        consultations = list(tx.run(_CONSULTATIONS_QUERY, activity_id=activity_id))
        return activity_record["a"], consultations

    with driver.session() as session:
        result = session.execute_read(_read)

    if result is None:
        return None

    activity_node, consultations = result

    return ActivityDetails.from_records(activity_node, consultations)
