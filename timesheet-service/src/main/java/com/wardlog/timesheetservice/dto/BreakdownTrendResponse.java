package com.wardlog.timesheetservice.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.util.List;

@Getter
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class BreakdownTrendResponse {

    private LocalDate from;

    private LocalDate to;

    private boolean bucketed;

    private List<TrendBucket> buckets;
}
