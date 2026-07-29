package com.wardlog.timesheetservice.dto;

import java.time.Instant;
import java.util.UUID;

public record MonthClosureResponse(

        UUID id,

        UUID doctorId,

        int year,

        int month,

        Instant closedAt
) {
}
