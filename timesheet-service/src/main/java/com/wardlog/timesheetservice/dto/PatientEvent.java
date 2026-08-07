package com.wardlog.timesheetservice.dto;

import java.util.List;
import java.util.UUID;

/**
 * Payload consumed from the "ai-to-timesheet-patient" Kafka topic. Field names are a
 * cross-service contract with the Python producer (ai-service) — do not rename without
 * updating both sides.
 */
public record PatientEvent(
        UUID activityId,
        PatientPayload patient
) {

    public record PatientPayload(
            String name,
            Integer age,
            String sex,
            List<String> diagnosis,
            List<String> drugs
    ) {
    }
}
