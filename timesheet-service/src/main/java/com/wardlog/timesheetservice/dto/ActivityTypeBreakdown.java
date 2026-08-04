package com.wardlog.timesheetservice.dto;

import com.wardlog.timesheetservice.enums.ActivityType;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class ActivityTypeBreakdown {

    private ActivityType activityType;

    private String label;

    private long activityCount;

    private long totalMinutes;
}
