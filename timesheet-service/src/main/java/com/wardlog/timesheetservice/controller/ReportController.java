package com.wardlog.timesheetservice.controller;

import com.wardlog.timesheetservice.dto.ActivityComparisonResponse;
import com.wardlog.timesheetservice.dto.ActivityTrendsResponse;
import com.wardlog.timesheetservice.dto.BreakdownTrendResponse;
import com.wardlog.timesheetservice.dto.GapsReportResponse;
import com.wardlog.timesheetservice.exception.InvalidActivityPayloadException;
import com.wardlog.timesheetservice.service.ReportService;
import lombok.RequiredArgsConstructor;

import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;

/**
 * Home for Timesheet-derived reports. First report is activity comparison; more will
 * be added here rather than bolted onto {@link ActivityController}.
 */
@RestController
@RequestMapping("/api/v1/reports")
@RequiredArgsConstructor
public class ReportController {

    private final ReportService reportService;

    @GetMapping("/activity-comparison")
    public ResponseEntity<ActivityComparisonResponse> getActivityComparison(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate from,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate to) {

        if (from.isAfter(to)) {
            throw new InvalidActivityPayloadException(
                    "'from' (" + from + ") must not be after 'to' (" + to + ")");
        }

        ActivityComparisonResponse response = reportService.activityComparison(from, to);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/gaps")
    public ResponseEntity<GapsReportResponse> getGaps(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate from,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate to) {

        if (from.isAfter(to)) {
            throw new InvalidActivityPayloadException(
                    "'from' (" + from + ") must not be after 'to' (" + to + ")");
        }

        GapsReportResponse response = reportService.gapsReport(from, to);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/breakdown-trend")
    public ResponseEntity<BreakdownTrendResponse> getBreakdownTrend(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate from,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate to) {

        if (from.isAfter(to)) {
            throw new InvalidActivityPayloadException(
                    "'from' (" + from + ") must not be after 'to' (" + to + ")");
        }

        BreakdownTrendResponse response = reportService.breakdownTrend(from, to);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/activity-trends")
    public ResponseEntity<ActivityTrendsResponse> getActivityTrends(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate from,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate to) {

        if (from.isAfter(to)) {
            throw new InvalidActivityPayloadException(
                    "'from' (" + from + ") must not be after 'to' (" + to + ")");
        }

        ActivityTrendsResponse response = reportService.activityTrends(from, to);
        return ResponseEntity.ok(response);
    }
}
