package com.wardlog.timesheetservice.dto;

import java.time.Instant;

public record MonthStatusResponse(

        boolean closed,

        Instant closedAt
) {
}
