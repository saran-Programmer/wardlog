package com.wardlog.timesheetservice.service;

import com.wardlog.timesheetservice.dto.CloseMonthRequest;
import com.wardlog.timesheetservice.dto.MonthClosureResponse;
import com.wardlog.timesheetservice.dto.MonthStatusResponse;

import java.time.LocalDateTime;
import java.util.UUID;

public interface TimesheetClosureService {

    MonthClosureResponse closeMonth(CloseMonthRequest request);

    MonthStatusResponse getStatus(UUID doctorId, int year, int month);

    /**
     * Guard called from the activity flow before an activity is persisted. Throws if the
     * month owning {@code activityStart} (its month only — never endDateTime) is closed.
     */
    void assertMonthOpenForActivity(UUID doctorId, LocalDateTime activityStart);
}
