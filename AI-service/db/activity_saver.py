from graph.config import DoctorContext
from graph.models.activity import Activity

from .connection import driver

_WRITE_LOGGED_ACTIVITY_QUERY = """
MERGE (d:Doctor {id: $doctor_id})
  SET d.name = $doctor_name, d.age = $doctor_age, d.sex = $doctor_sex
MERGE (a:Activity {id: $activity_id, doctorId: $doctor_id})
  SET a.name = $activity_name,
      a.start = $activity_start,
      a.end = $activity_end,
      a.location = $activity_location,
      a.notes = $activity_notes
MERGE (d)-[:LOGGED]->(a)
"""


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
