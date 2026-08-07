from typing import Optional

from graph.models.patient_details import PatientDetails

from .connection import driver
from .normalize import normalize_key

_PATIENT_QUERY = "MATCH (p:Patient {key: $patient_key, doctorId: $doctor_id}) RETURN p"

_CONSULTATIONS_QUERY = """
MATCH (p:Patient {key: $patient_key, doctorId: $doctor_id})<-[:WITH_PATIENT]-(c:Consultation {doctorId: $doctor_id})
OPTIONAL MATCH (c)-[:HAS_DIAGNOSIS]->(dx:Diagnosis {doctorId: $doctor_id})
OPTIONAL MATCH (c)-[:PRESCRIBED]->(dr:Drug {doctorId: $doctor_id})
OPTIONAL MATCH (c)-[:SURGERY_TYPE]->(st:SurgeryType {doctorId: $doctor_id})
OPTIONAL MATCH (a:Activity {doctorId: $doctor_id})-[:HAS_CONSULTATION]->(c)
RETURN c.id AS consultation_id,
       collect(DISTINCT dx.name) AS diagnoses,
       collect(DISTINCT dr.name) AS drugs,
       st.name AS surgery_type,
       a.name AS activity_name,
       a.start AS activity_start,
       a.end AS activity_end,
       a.location AS activity_location
"""

_REPORTS_QUERY = """
MATCH (p:Patient {key: $patient_key, doctorId: $doctor_id})-[:HAS_REPORT]->(r:Report {doctorId: $doctor_id})
RETURN r.report_type AS report_type,
       r.report_date AS report_date,
       r.findings AS findings,
       r.notes AS notes
"""


def find_patient_details(doctor_id: str, patient_name: str) -> Optional[PatientDetails]:
    patient_key = normalize_key(patient_name)

    def _read(tx):
        patient_record = tx.run(
            _PATIENT_QUERY, patient_key=patient_key, doctor_id=doctor_id
        ).single()
        if patient_record is None:
            return None

        consultations = list(
            tx.run(_CONSULTATIONS_QUERY, patient_key=patient_key, doctor_id=doctor_id)
        )
        reports = list(
            tx.run(_REPORTS_QUERY, patient_key=patient_key, doctor_id=doctor_id)
        )
        return patient_record["p"], consultations, reports

    with driver.session() as session:
        result = session.execute_read(_read)

    if result is None:
        return None

    patient_node, consultations, reports = result

    return PatientDetails.from_records(patient_node, consultations, reports)
