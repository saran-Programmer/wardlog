package com.wardlog.timesheetservice.controller;

import com.wardlog.timesheetservice.dto.CloseMonthRequest;
import com.wardlog.timesheetservice.dto.MonthClosureResponse;
import com.wardlog.timesheetservice.dto.MonthStatusResponse;
import com.wardlog.timesheetservice.exception.MissingDoctorHeaderException;
import com.wardlog.timesheetservice.service.TimesheetClosureService;
import com.wardlog.timesheetservice.validation.MonthClosureValidator;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/timesheet")
@RequiredArgsConstructor
public class TimesheetClosureController {

    private final MonthClosureValidator monthClosureValidator;
    private final TimesheetClosureService timesheetClosureService;

    @PostMapping("/close")
    public ResponseEntity<MonthClosureResponse> closeMonth(
            @RequestHeader(value = "X-Doctor-Id", required = false) UUID doctorId,
            @Valid @RequestBody CloseMonthRequest request) {

        UUID resolvedDoctorId = requireDoctorId(doctorId);
        monthClosureValidator.validateClose(request);
        MonthClosureResponse response = timesheetClosureService.closeMonth(request, resolvedDoctorId);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/status")
    public ResponseEntity<MonthStatusResponse> getStatus(
            @RequestHeader(value = "X-Doctor-Id", required = false) UUID doctorId,
            @RequestParam int year,
            @RequestParam int month) {

        UUID resolvedDoctorId = requireDoctorId(doctorId);
        MonthStatusResponse response = timesheetClosureService.getStatus(resolvedDoctorId, year, month);
        return ResponseEntity.ok(response);
    }

    private UUID requireDoctorId(UUID doctorId) {
        if (doctorId == null) {
            throw new MissingDoctorHeaderException("Missing X-Doctor-Id header");
        }
        return doctorId;
    }
}
