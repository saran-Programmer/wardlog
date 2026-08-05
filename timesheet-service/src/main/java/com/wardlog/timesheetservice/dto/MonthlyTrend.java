package com.wardlog.timesheetservice.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

@Getter
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class MonthlyTrend {

    private String month;

    private List<ActivityTypeBreakdown> breakdown;
}
