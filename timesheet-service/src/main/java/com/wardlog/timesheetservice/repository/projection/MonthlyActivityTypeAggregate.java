package com.wardlog.timesheetservice.repository.projection;

import com.wardlog.timesheetservice.enums.ActivityType;

public interface MonthlyActivityTypeAggregate {

    String getMonth();

    ActivityType getActivityType();

    long getActivityCount();

    long getTotalMinutes();
}
