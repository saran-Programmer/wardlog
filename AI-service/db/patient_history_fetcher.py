from typing import Optional

from graph.models.patient_history import PatientHistory

from .connection import driver

_PATIENT_QUERY = "MATCH (p:Patient {id: $patient_id, doctorId: $doctor_id}) RETURN p"

_CONSULTATIONS_QUERY = """
MATCH (a:Activity {doctorId: $doctor_id})-[:HAS_CONSULTATION]->(c:Consultation {doctorId: $doctor_id})-[:WITH_PATIENT]->(p:Patient {id: $patient_id, doctorId: $doctor_id})
OPTIONAL MATCH (c)-[:HAS_DIAGNOSIS]->(dx:Diagnosis {doctorId: $doctor_id})
OPTIONAL MATCH (c)-[:PRESCRIBED]->(dr:Drug {doctorId: $doctor_id})
OPTIONAL MATCH (c)-[:SURGERY_TYPE]->(st:SurgeryType {doctorId: $doctor_id})
RETURN c.id AS consultation_id,
       collect(DISTINCT dx.name) AS diagnoses,
       collect(DISTINCT dr.name) AS drugs,
       st.name AS surgery_type,
       a AS activity
"""

_REPORTS_QUERY = """
MATCH (p:Patient {id: $patient_id, doctorId: $doctor_id})-[:HAS_REPORT]->(r:Report {doctorId: $doctor_id})
RETURN r.report_type AS report_type,
       r.report_date AS report_date,
       r.findings AS findings,
       r.notes AS notes,
       r.file_url AS file_url
"""


def get_patient_history(doctor_id: str, patient_id: str) -> Optional[PatientHistory]:
    """Read-only nested fetch of a patient's full history: every consultation
    (with its diagnoses, drugs, surgery type, and the owning activity as the
    visit) plus every report. Mirrors find_activity_details, but rooted at
    Patient instead of Activity.

    doctor_id is always code-injected, never taken from LLM input, and scopes
    the patient lookup plus every traversed node. Returns None if no patient
    with this id/doctorId pair exists; a patient with no consultations or
    reports still returns with empty lists.

    Patient histories can grow large; a recent-N or date-bound limit may be
    added later. For now this returns everything.
    """

    def _read(tx):
        patient_record = tx.run(
            _PATIENT_QUERY, patient_id=patient_id, doctor_id=doctor_id
        ).single()
        if patient_record is None:
            return None

        consultations = list(
            tx.run(_CONSULTATIONS_QUERY, patient_id=patient_id, doctor_id=doctor_id)
        )
        reports = list(
            tx.run(_REPORTS_QUERY, patient_id=patient_id, doctor_id=doctor_id)
        )
        return patient_record["p"], consultations, reports

    with driver.session() as session:
        result = session.execute_read(_read)

    if result is None:
        return None

    patient_node, consultations, reports = result

    return PatientHistory.from_records(patient_node, consultations, reports)
