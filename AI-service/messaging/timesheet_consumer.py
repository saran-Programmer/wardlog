import json
import logging
import os
import threading
from typing import Optional

from kafka import KafkaConsumer
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)

TOPIC = "timesheet-to-ai-activity"
_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BROKER")

_neo4j_driver = GraphDatabase.driver(
    os.environ["NEO4J_URI"],
    auth=(os.environ["NEO4J_USERNAME"], os.environ["NEO4J_PASSWORD"]),
)

# Maps the timesheet-service ActivityType enum values to the AI-service
# Activity.name literals ("surgeryblock" | "clinicblock" | "oncall" | "onsiteoncall").
_ACTIVITY_TYPE_MAP = {
    "CLINIC_BLOCK": "clinicblock",
    "ON_CALL": "oncall",
    "ON_SITE_ON_CALL": "onsiteoncall",
    "SURGERY_BLOCK": "surgeryblock",
}


def _to_ai_activity_type(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    mapped = _ACTIVITY_TYPE_MAP.get(value)
    if mapped is None:
        raise ValueError(f"Unknown activityType from timesheet: {value!r}")
    return mapped


_CREATE_ACTIVITY_QUERY = """
MERGE (d:Doctor {id: $doctor_id})
MERGE (a:Activity {id: $activity_id, doctorId: $doctor_id})
  SET a.name = $activity_type,
      a.start = $start_date_time,
      a.end = $end_date_time,
      a.location = $location,
      a.notes = $notes
MERGE (d)-[:LOGGED]->(a)
"""

_UPDATE_ACTIVITY_QUERY = """
MATCH (a:Activity {id: $activity_id, doctorId: $doctor_id})
  SET a.name = $activity_type,
      a.start = $start_date_time,
      a.end = $end_date_time,
      a.location = $location,
      a.notes = $notes
"""

_DELETE_ACTIVITY_QUERY = """
MATCH (a:Activity {id: $activity_id, doctorId: $doctor_id})
DETACH DELETE a
"""


def _handle_created(event: dict) -> None:
    def _write(tx):
        tx.run(
            _CREATE_ACTIVITY_QUERY,
            activity_id=event["activityId"],
            doctor_id=event["doctorId"],
            activity_type=_to_ai_activity_type(event.get("activityType")),
            start_date_time=event.get("startDateTime"),
            end_date_time=event.get("endDateTime"),
            location=event.get("location"),
            notes=event.get("notes"),
        )

    with _neo4j_driver.session() as session:
        session.execute_write(_write)


def _handle_updated(event: dict) -> None:
    def _write(tx):
        tx.run(
            _UPDATE_ACTIVITY_QUERY,
            activity_id=event["activityId"],
            doctor_id=event["doctorId"],
            activity_type=_to_ai_activity_type(event.get("activityType")),
            start_date_time=event.get("startDateTime"),
            end_date_time=event.get("endDateTime"),
            location=event.get("location"),
            notes=event.get("notes"),
        )

    with _neo4j_driver.session() as session:
        session.execute_write(_write)


def _handle_deleted(event: dict) -> None:
    def _write(tx):
        tx.run(
            _DELETE_ACTIVITY_QUERY,
            activity_id=event["activityId"],
            doctor_id=event["doctorId"],
        )

    with _neo4j_driver.session() as session:
        session.execute_write(_write)


_HANDLERS = {
    "CREATED": _handle_created,
    "UPDATED": _handle_updated,
    "DELETED": _handle_deleted,
}


def _consume_loop(stop_event: threading.Event) -> None:
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=_BOOTSTRAP_SERVERS,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        enable_auto_commit=False,
        group_id="ai-service-timesheet-sync",
    )
    try:
        while not stop_event.is_set():
            records = consumer.poll(timeout_ms=1000)
            if not records:
                continue
            for _partition, messages in records.items():
                for message in messages:
                    event = message.value
                    event_type = event.get("eventType")
                    activity_id = event.get("activityId")
                    logger.info(
                        "Consumed timesheet event: eventType=%s activityId=%s",
                        event_type,
                        activity_id,
                    )
                    handler = _HANDLERS.get(event_type)
                    if handler is None:
                        logger.error(
                            "Unknown eventType=%s activityId=%s — skipping and committing",
                            event_type,
                            activity_id,
                        )
                        consumer.commit()
                        continue
                    try:
                        handler(event)
                    except Exception:
                        logger.error(
                            "Neo4j write failed for eventType=%s activityId=%s — "
                            "not committing offset, will retry",
                            event_type,
                            activity_id,
                            exc_info=True,
                        )
                        continue
                    logger.info(
                        "Neo4j write succeeded: eventType=%s activityId=%s",
                        event_type,
                        activity_id,
                    )
                    consumer.commit()
    finally:
        consumer.close()
        _neo4j_driver.close()


_stop_event = threading.Event()


def start_timesheet_consumer() -> None:
    thread = threading.Thread(
        target=_consume_loop, args=(_stop_event,), daemon=True
    )
    thread.start()


def stop_timesheet_consumer() -> None:
    _stop_event.set()