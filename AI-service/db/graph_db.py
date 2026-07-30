import os

from neo4j import GraphDatabase

from graph.config import DoctorContext
from graph.models.activity import Activity

driver = GraphDatabase.driver(
    os.environ["NEO4J_URI"],
    auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
)

_WRITE_LOGGED_ACTIVITY_QUERY = """
MERGE (d:Doctor {id: $doctor_id})
  SET d.name = $doctor_name, d.age = $doctor_age, d.sex = $doctor_sex
MERGE (a:Activity {id: $activity_id})
  SET a.name = $activity_name,
      a.start = $activity_start,
      a.end = $activity_end,
      a.location = $activity_location,
      a.notes = $activity_notes
MERGE (d)-[:LOGGED]->(a)
"""


def verify_connection() -> None:
    driver.verify_connectivity()


def close_driver() -> None:
    driver.close()


def write_logged_activity(doctor: DoctorContext, activity: Activity) -> None:
    def _write(tx):
        tx.run(
            _WRITE_LOGGED_ACTIVITY_QUERY,
            doctor_id=doctor.id,
            doctor_name=doctor.name,
            doctor_age=doctor.age,
            doctor_sex=doctor.sex,
            activity_id=activity.id,
            activity_name=activity.name,
            activity_start=activity.start.isoformat() if activity.start else None,
            activity_end=activity.end.isoformat() if activity.end else None,
            activity_location=activity.location,
            activity_notes=activity.notes,
        )

    with driver.session() as session:
        session.execute_write(_write)
