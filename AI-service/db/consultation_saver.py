from uuid import uuid4

from graph.models.consultation import Consultation

from .connection import driver
from .normalize import normalize_key

_WRITE_CONSULTATION_QUERY = """
MATCH (a:Activity {id: $activity_id, doctorId: $doctor_id})
CREATE (c:Consultation {id: $consultation_id, doctorId: $doctor_id})
MERGE (a)-[:HAS_CONSULTATION]->(c)
MERGE (p:Patient {key: $patient_key, doctorId: $doctor_id})
  ON CREATE SET p.id = $patient_id
  SET p.name = $patient_name,
      p.age = coalesce($patient_age, p.age),
      p.sex = coalesce($patient_sex, p.sex),
      p.patientReferenceId = coalesce($patient_reference_id, p.patientReferenceId)
MERGE (c)-[:WITH_PATIENT]->(p)
FOREACH (diagnosis IN $diagnoses |
  MERGE (dx:Diagnosis {key: diagnosis.key, doctorId: $doctor_id})
    SET dx.name = diagnosis.name
  MERGE (c)-[:HAS_DIAGNOSIS]->(dx)
)
FOREACH (drug IN $drugs |
  MERGE (dr:Drug {key: drug.key, doctorId: $doctor_id})
    SET dr.name = drug.name
  MERGE (c)-[:PRESCRIBED]->(dr)
)
FOREACH (_ IN CASE WHEN $surgery_type IS NOT NULL THEN [1] ELSE [] END |
  MERGE (st:SurgeryType {key: $surgery_type.key, doctorId: $doctor_id})
    SET st.name = $surgery_type.name
  MERGE (c)-[:SURGERY_TYPE]->(st)
)
RETURN p.id AS patient_id
"""


def save_consultation(doctor_id: str, activity_id: str, consultation: Consultation) -> str:
    consultation_id = str(uuid4())

    patient = consultation.patient
    patient_id = str(uuid4())

    def _write(tx):
        result = tx.run(
            _WRITE_CONSULTATION_QUERY,
            doctor_id=doctor_id,
            activity_id=activity_id,
            consultation_id=consultation_id,
            patient_id=patient_id,
            patient_key=normalize_key(patient.name) if patient else None,
            patient_name=patient.name if patient else None,
            patient_age=patient.age if patient else None,
            patient_sex=patient.sex if patient else None,
            patient_reference_id=patient.patient_reference_id if patient else None,
            diagnoses=[
                {"key": normalize_key(name), "name": name}
                for name in consultation.diagnoses
            ],
            drugs=[
                {"key": normalize_key(name), "name": name} for name in consultation.drugs
            ],
            surgery_type=(
                {
                    "key": normalize_key(consultation.surgery_type),
                    "name": consultation.surgery_type,
                }
                if consultation.surgery_type is not None
                else None
            ),
        )
        return result.single()["patient_id"]

    with driver.session() as session:
        return session.execute_write(_write)
