package com.wardlog.timesheetservice.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.YearMonth;
import java.util.List;

@Getter
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class GapsReportResponse {

    private LocalDate from;

    private LocalDate to;

    private YearMonth anchorMonth;

    private List<YearMonth> lookbackMonths;

    private List<GapEntry> gaps;
}
