package com.wardlog.timesheetservice.controller;

import com.wardlog.timesheetservice.dto.ActivityListResponse;
import com.wardlog.timesheetservice.dto.ActivityResponse;
import com.wardlog.timesheetservice.dto.CreateActivityRequest;
import com.wardlog.timesheetservice.dto.UpdateActivityRequest;
import com.wardlog.timesheetservice.enums.ActivityType;
import com.wardlog.timesheetservice.exception.MissingDoctorHeaderException;
import com.wardlog.timesheetservice.service.ActivityService;
import com.wardlog.timesheetservice.validation.ActivityValidator;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/activities")
@RequiredArgsConstructor
public class ActivityController {

    private final ActivityValidator activityValidator;
    private final ActivityService activityService;

    @PostMapping(consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<ActivityResponse> createActivity(
            @RequestHeader(value = "X-Doctor-Id", required = false) UUID doctorId,
            @Valid @RequestPart("activity") CreateActivityRequest request,
            @RequestPart(value = "files", required = false) List<MultipartFile> files) {

        UUID resolvedDoctorId = requireDoctorId(doctorId);
        activityValidator.validateCreate(request);
        ActivityResponse response = activityService.createActivity(request, resolvedDoctorId, files);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/{activityId}")
    public ResponseEntity<ActivityResponse> getActivityById(@PathVariable UUID activityId) {
        ActivityResponse response = activityService.getActivityById(activityId);
        return ResponseEntity.ok(response);
    }

    @PutMapping(value = "/{activityId}", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<ActivityResponse> updateActivity(
            @PathVariable UUID activityId,
            @Valid @RequestPart("activity") UpdateActivityRequest request,
            @RequestPart(value = "newFiles", required = false) List<MultipartFile> newFiles,
            @RequestParam(value = "removeDocumentIds", required = false) List<UUID> removeDocumentIds) {

        activityValidator.validateUpdate(request);

        ActivityResponse response = activityService.updateActivity(activityId, request, newFiles, removeDocumentIds);
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
            @RequestHeader(value = "X-Doctor-Id", required = false) UUID doctorId) {

        UUID resolvedDoctorId = requireDoctorId(doctorId);
        ActivityListResponse response = activityService.getActivities(startDate, endDate, activityTypes, resolvedDoctorId);
        return ResponseEntity.ok(response);
    }

    private UUID requireDoctorId(UUID doctorId) {
        if (doctorId == null) {
            throw new MissingDoctorHeaderException("Missing X-Doctor-Id header");
        }
        return doctorId;
    }
}
