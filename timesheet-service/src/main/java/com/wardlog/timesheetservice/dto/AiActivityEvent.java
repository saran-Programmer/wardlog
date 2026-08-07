package com.wardlog.timesheetservice.dto;

import com.wardlog.timesheetservice.enums.ActivityType;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Shape of the ai-to-timesheet-activity Kafka message published by the AI Service
 * (see ai-service/messaging/kafka_producer.py:publish_activity). Unlike the HTTP
 * create path, this message has no request header to carry doctorId, so the AI
 * Service puts it in the payload itself.
 */
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AiActivityEvent {

    private UUID id;

    private UUID doctorId;

    private ActivityType activityType;

    private LocalDateTime startDateTime;

    private LocalDateTime endDateTime;

    private String location;

    private String notes;

    public CreateActivityRequest toCreateActivityRequest() {
        return CreateActivityRequest.builder()
                .id(id)
                .activityType(activityType)
                .startDateTime(startDateTime)
                .endDateTime(endDateTime)
                .location(location)
                .notes(notes)
                .build();
    }
}
