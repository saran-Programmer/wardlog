package com.wardlog.timesheetservice.repository.projection;

import com.wardlog.timesheetservice.enums.ActivityType;

public interface ActivityTypeAggregate {

    ActivityType getActivityType();

    long getActivityCount();

    long getTotalMinutes();
}
