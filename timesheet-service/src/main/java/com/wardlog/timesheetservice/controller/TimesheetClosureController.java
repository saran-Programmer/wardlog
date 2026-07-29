package com.wardlog.timesheetservice.controller;

import com.wardlog.timesheetservice.dto.CloseMonthRequest;
import com.wardlog.timesheetservice.dto.MonthClosureResponse;
import com.wardlog.timesheetservice.dto.MonthStatusResponse;
import com.wardlog.timesheetservice.service.TimesheetClosureService;
import com.wardlog.timesheetservice.validation.MonthClosureValidator;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
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
    public ResponseEntity<MonthClosureResponse> closeMonth(@Valid @RequestBody CloseMonthRequest request) {
        monthClosureValidator.validateClose(request);
        MonthClosureResponse response = timesheetClosureService.closeMonth(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/status")
    public ResponseEntity<MonthStatusResponse> getStatus(

            // WORKAROUND: doctorId is accepted as a query param for now. In the real
            // implementation this must be derived from the auth token, not trusted from the request.
            @RequestParam UUID doctorId,
            @RequestParam int year,
            @RequestParam int month) {

        MonthStatusResponse response = timesheetClosureService.getStatus(doctorId, year, month);
        return ResponseEntity.ok(response);
    }
}
