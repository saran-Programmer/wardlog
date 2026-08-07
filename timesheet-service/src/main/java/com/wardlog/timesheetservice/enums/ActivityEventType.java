package com.wardlog.timesheetservice.enums;

/**
 * Kafka event kind published to "timesheet-to-ai-activity". Names must match the
 * string literals the Python consumer's _HANDLERS dict keys on
 * (ai-service/messaging/timesheet_consumer.py) — Jackson serializes this as .name().
 */
public enum ActivityEventType {
    CREATED,
    UPDATED,
    DELETED
}
