package com.wardlog.timesheetservice.dto;

import com.wardlog.timesheetservice.enums.ActivityEventType;
import com.wardlog.timesheetservice.enums.ActivityType;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Payload published to the "timesheet-to-ai-activity" Kafka topic for the AI Service
 * to consume. Field names are a cross-service contract with the Python consumer
 * (ai-service/messaging/timesheet_consumer.py) — do not rename without updating both sides.
 */
public record ActivityEvent(
        ActivityEventType eventType,
        UUID activityId,
        UUID doctorId,
        ActivityType activityType,
        LocalDateTime startDateTime,
        LocalDateTime endDateTime,
        String location,
        String notes
) {
}
