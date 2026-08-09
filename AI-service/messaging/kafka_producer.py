import json
import logging
import os
from typing import Optional
from uuid import UUID

from kafka import KafkaProducer

logger = logging.getLogger(__name__)

TOPIC_ACTIVITY = "ai-to-timesheet-activity"
TOPIC_PATIENT = "ai-to-timesheet-patient"

_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BROKER")

_producer: Optional[KafkaProducer] = None


def _get_producer() -> KafkaProducer:
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            acks="all",
            retries=3,
        )
    return _producer


def _publish(topic: str, key: UUID, value: dict) -> None:
    key_bytes = str(key).encode("utf-8")
    try:
        _get_producer().send(topic, key=key_bytes, value=value).get()
    except Exception:
        logger.error(
            "Kafka publish failed: topic=%s key=%s — data saved in Neo4j but publish failed",
            topic,
            key,
            exc_info=True,
        )
        return

    logger.info("Kafka publish succeeded: topic=%s key=%s", topic, key)


def publish_activity(
    id: UUID,
    doctorId: UUID,
    activityType: str,
    startDateTime,
    endDateTime,
    location: Optional[str] = None,
    notes: Optional[str] = None,
) -> None:
    payload = {
        "id": str(id),
        "doctorId": str(doctorId),
        "activityType": activityType,
        "startDateTime": startDateTime.isoformat(),
        "endDateTime": endDateTime.isoformat(),
        "location": location,
        "notes": notes,
    }
    _publish(TOPIC_ACTIVITY, id, payload)


def publish_patient(
    activityId: UUID,
    name: Optional[str] = None,
    age: Optional[int] = None,
    sex: Optional[str] = None,
    diagnosis: Optional[list[str]] = None,
    drugs: Optional[list[str]] = None,
) -> None:
    payload = {
        "activityId": str(activityId),
        "patient": {
            "name": name,
            "age": age,
            "sex": sex,
            "diagnosis": diagnosis or [],
            "drugs": drugs or [],
        },
    }
    _publish(TOPIC_PATIENT, activityId, payload)
