package com.wardlog.timesheetservice.controller;

import com.wardlog.timesheetservice.dto.ActivityListResponse;
import com.wardlog.timesheetservice.dto.ActivityResponse;
import com.wardlog.timesheetservice.dto.CreateActivityRequest;
import com.wardlog.timesheetservice.dto.UpdateActivityRequest;
import com.wardlog.timesheetservice.enums.ActivityType;
import com.wardlog.timesheetservice.service.ActivityService;
import com.wardlog.timesheetservice.validation.ActivityValidator;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/activities")
@RequiredArgsConstructor
public class ActivityController {

    private final ActivityValidator activityValidator;
    private final ActivityService activityService;

    @PostMapping
    public ResponseEntity<ActivityResponse> createActivity(@Valid @RequestBody CreateActivityRequest request) {
        activityValidator.validateCreate(request);
        ActivityResponse response = activityService.createActivity(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/{activityId}")
    public ResponseEntity<ActivityResponse> getActivityById(@PathVariable UUID activityId) {
        ActivityResponse response = activityService.getActivityById(activityId);
        return ResponseEntity.ok(response);
    }

    @PutMapping("/{activityId}")
    public ResponseEntity<ActivityResponse> updateActivity(
            @PathVariable UUID activityId, @Valid @RequestBody UpdateActivityRequest request) {

        activityValidator.validateUpdate(request);
        
        ActivityResponse response = activityService.updateActivity(activityId, request);
        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/{activityId}")
    public ResponseEntity<Void> deleteActivity(@PathVariable UUID activityId) {
        activityService.deleteActivity(activityId);
        return ResponseEntity.noContent().build();
    }

    @GetMapping
    public ResponseEntity<ActivityListResponse> getActivities(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate,
            @RequestParam(required = false) List<ActivityType> activityTypes,

            // WORKAROUND: doctorId is accepted as a query param for now. In the real
            // implementation this must be derived from the auth token, not trusted from the request.
            @RequestParam(required = false) UUID doctorId) {
                
        ActivityListResponse response = activityService.getActivities(startDate, endDate, activityTypes, doctorId);
        return ResponseEntity.ok(response);
    }
}
