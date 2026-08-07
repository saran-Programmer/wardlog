package com.wardlog.timesheetservice.dto;

import com.wardlog.timesheetservice.enums.ActivityType;

import java.time.Instant;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

public record ActivityResponse(

        UUID id,

        UUID doctorId,

        ActivityType activityType,

        LocalDateTime startDateTime,

        LocalDateTime endDateTime,

        Long durationMinutes,

        String location,

        String notes,

        Instant createdDate,

        Instant lastModifiedDate,

        List<DocumentResponse> documents
) {
}
