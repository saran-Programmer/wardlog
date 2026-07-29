package com.wardlog.timesheetservice.dto;

import com.wardlog.timesheetservice.enums.ActivityType;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.UUID;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CreateActivityRequest {

    // Optional — may be supplied (AI path) or null (UI path).
    private UUID id;

    // WORKAROUND: doctorId is accepted in the payload for now. In the real implementation
    // this must be derived from the auth token, not trusted from the request body.
    @NotNull
    private UUID doctorId;

    @NotNull
    private ActivityType activityType;

    @NotNull
    private LocalDateTime startDateTime;

    @NotNull
    private LocalDateTime endDateTime;

    private String location;

    private String notes;
}
