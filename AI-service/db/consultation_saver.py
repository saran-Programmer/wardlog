from uuid import uuid4

from graph.models.consultation import Consultation

from .connection import driver

_WRITE_CONSULTATION_QUERY = """
MATCH (a:Activity {id: $activity_id})
CREATE (c:Consultation {id: $consultation_id})
MERGE (a)-[:HAS_CONSULTATION]->(c)
FOREACH (_ IN CASE WHEN $patient_name IS NOT NULL THEN [1] ELSE [] END |
  MERGE (p:Patient {name: $patient_name})
    SET p.age = coalesce($patient_age, p.age), p.sex = coalesce($patient_sex, p.sex)
  MERGE (c)-[:WITH_PATIENT]->(p)
)
FOREACH (diagnosis IN $diagnoses |
  MERGE (dx:Diagnosis {key: diagnosis.key})
    SET dx.name = diagnosis.name
  MERGE (c)-[:HAS_DIAGNOSIS]->(dx)
)
FOREACH (drug IN $drugs |
  MERGE (dr:Drug {key: drug.key})
    SET dr.name = drug.name
  MERGE (c)-[:PRESCRIBED]->(dr)
)
FOREACH (_ IN CASE WHEN $surgery_type IS NOT NULL THEN [1] ELSE [] END |
  MERGE (st:SurgeryType {key: $surgery_type.key})
    SET st.name = $surgery_type.name
  MERGE (c)-[:SURGERY_TYPE]->(st)
)
"""


def _normalize(text: str) -> str:
    return text.lower().replace(" ", "")


def save_consultation(activity_id: str, consultation: Consultation) -> str:
    consultation_id = str(uuid4())

    patient = consultation.patient

    def _write(tx):
        tx.run(
            _WRITE_CONSULTATION_QUERY,
            activity_id=activity_id,
            consultation_id=consultation_id,
            patient_name=patient.name if patient else None,
            patient_age=patient.age if patient else None,
            patient_sex=patient.sex if patient else None,
            diagnoses=[
                {"key": _normalize(name), "name": name}
                for name in consultation.diagnoses
            ],
            drugs=[
                {"key": _normalize(name), "name": name} for name in consultation.drugs
            ],
            surgery_type=(
                {
                    "key": _normalize(consultation.surgery_type),
                    "name": consultation.surgery_type,
                }
                if consultation.surgery_type is not None
                else None
            ),
        )

    with driver.session() as session:
        session.execute_write(_write)

    return consultation_id
