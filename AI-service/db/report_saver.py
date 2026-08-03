from uuid import uuid4

from graph.models.report_extraction import ReportExtraction

from .connection import driver
from .normalize import normalize_key

_WRITE_REPORT_QUERY = """
MERGE (p:Patient {key: $patient_key})
  SET p.name = $patient_name
CREATE (r:Report {
  id: $id,
  report_type: $report_type,
  report_date: $report_date,
  findings: $findings,
  full_text: $full_text,
  notes: $doctor_notes
})
MERGE (p)-[:HAS_REPORT]->(r)
"""


def save_report(report: ReportExtraction) -> str:
    report_id = str(uuid4())

    def _write(tx):
        tx.run(
            _WRITE_REPORT_QUERY,
            patient_key=normalize_key(report.patient_name),
            patient_name=report.patient_name,
            id=report_id,
            report_type=report.report_type,
            report_date=report.report_date.isoformat() if report.report_date else None,
            findings=report.findings,
            full_text=report.full_text,
            doctor_notes=report.doctor_notes,
        )

    with driver.session() as session:
        session.execute_write(_write)

    return report_id
