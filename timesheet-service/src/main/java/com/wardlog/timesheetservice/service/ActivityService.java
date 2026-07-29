package com.wardlog.timesheetservice.service;

import com.wardlog.timesheetservice.dto.ActivityListResponse;
import com.wardlog.timesheetservice.dto.ActivityMetaResponse;
import com.wardlog.timesheetservice.dto.ActivityResponse;
import com.wardlog.timesheetservice.dto.CreateActivityRequest;
import com.wardlog.timesheetservice.dto.UpdateActivityRequest;
import com.wardlog.timesheetservice.entity.Activity;
import com.wardlog.timesheetservice.enums.ActivityType;
import com.wardlog.timesheetservice.exception.ActivityNotFoundException;
import com.wardlog.timesheetservice.exception.ActivityOverlapException;
import com.wardlog.timesheetservice.repository.ActivityRepository;
import jakarta.persistence.criteria.Predicate;
import lombok.RequiredArgsConstructor;

import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class ActivityService {

    private final ActivityRepository activityRepository;
    private final TimesheetClosureService timesheetClosureService;

    public ActivityResponse createActivity(CreateActivityRequest request) {
        Activity activity = toEntity(request);

        // Closed-month enforcement point: an activity belongs to the month of its
        // startDateTime only. Edit/delete will reuse this same guard when built.
        timesheetClosureService.assertMonthOpenForActivity(request.getDoctorId(), request.getStartDateTime());

        if (activityRepository.existsOverlappingActivity(
                request.getDoctorId(), request.getStartDateTime(), request.getEndDateTime(), null)) {
            throw new ActivityOverlapException(
                    "Activity overlaps with an existing activity for this doctor");
        }

        Activity saved = activityRepository.save(activity);
        return toResponse(saved);
    }

    public ActivityResponse getActivityById(UUID activityId) {
        Activity activity = activityRepository.findById(activityId)
                .orElseThrow(() -> new ActivityNotFoundException("Activity not found: " + activityId));
        return toResponse(activity);
    }

    public ActivityResponse updateActivity(UUID activityId, UpdateActivityRequest request) {
        Activity existing = activityRepository.findById(activityId)
                .orElseThrow(() -> new ActivityNotFoundException("Activity not found: " + activityId));

        if (activityRepository.existsOverlappingActivity(
                existing.getDoctorId(), request.getStartDateTime(), request.getEndDateTime(), activityId)) {
            throw new ActivityOverlapException(
                    "Activity overlaps with an existing activity for this doctor");
        }

        existing.setActivityType(request.getActivityType());
        existing.setStartDateTime(request.getStartDateTime());
        existing.setEndDateTime(request.getEndDateTime());
        existing.setLocation(request.getLocation());
        existing.setNotes(request.getNotes());

        Activity saved = activityRepository.save(existing);
        return toResponse(saved);
    }

    public void deleteActivity(UUID activityId) {

        if (!activityRepository.existsById(activityId)) {
            
            throw new ActivityNotFoundException("Activity not found: " + activityId);
        }
        activityRepository.deleteById(activityId);
    }

    public ActivityListResponse getActivities(LocalDate startDate,
        LocalDate endDate, List<ActivityType> activityTypes, UUID doctorId) {
            
        Specification<Activity> spec = buildSpecification(startDate, endDate, activityTypes, doctorId);

        List<Activity> activities = activityRepository.findAll(spec);

        List<ActivityResponse> responses = activities.stream()
                .map(this::toResponse)
                .toList();

        ActivityMetaResponse meta = buildMeta(activities, activityTypes);

        return new ActivityListResponse(responses, meta);
    }

    private Specification<Activity> buildSpecification(LocalDate startDate,
         LocalDate endDate, List<ActivityType> activityTypes, UUID doctorId) {

        return (root, query, criteriaBuilder) -> {

            List<Predicate> predicates = new ArrayList<>();

            if (startDate != null) {
                predicates.add(criteriaBuilder.greaterThanOrEqualTo(
                        root.get("startDateTime"), startDate.atStartOfDay()));
            }

            if (endDate != null) {
                predicates.add(criteriaBuilder.lessThan(
                        root.get("startDateTime"), endDate.plusDays(1).atStartOfDay()));
            }

            if (activityTypes != null && !activityTypes.isEmpty()) {
                predicates.add(root.get("activityType").in(activityTypes));
            }

            // WORKAROUND: doctorId is accepted as a query param for now. In the real
            // implementation this must be derived from the auth token, not the request.
            if (doctorId != null) {
                predicates.add(criteriaBuilder.equal(root.get("doctorId"), doctorId));
            }

            return criteriaBuilder.and(predicates.toArray(new Predicate[0]));
        };
    }

    private ActivityMetaResponse buildMeta(List<Activity> activities, List<ActivityType> activityTypes) {
        Map<ActivityType, Long> summedMinutes = new EnumMap<>(ActivityType.class);
        for (Activity activity : activities) {
            summedMinutes.merge(activity.getActivityType(),
                    activity.getDurationMinutes() == null ? 0L : activity.getDurationMinutes(),
                    Long::sum);
        }

        boolean noFilter = activityTypes == null || activityTypes.isEmpty();

        return new ActivityMetaResponse(
                minutesFor(ActivityType.CLINIC_BLOCK, noFilter, activityTypes, summedMinutes),
                minutesFor(ActivityType.SURGERY_BLOCK, noFilter, activityTypes, summedMinutes),
                minutesFor(ActivityType.ON_CALL, noFilter, activityTypes, summedMinutes),
                minutesFor(ActivityType.ON_SITE_ON_CALL, noFilter, activityTypes, summedMinutes)
        );
    }

    private Long minutesFor(ActivityType type, boolean noFilter, List<ActivityType> activityTypes,
                             Map<ActivityType, Long> summedMinutes) {
        if (!noFilter && !activityTypes.contains(type)) {
            return -1L;
        }
        return summedMinutes.getOrDefault(type, 0L);
    }

    private Activity toEntity(CreateActivityRequest request) {
        return Activity.builder()
                .id(request.getId())
                .doctorId(request.getDoctorId())
                .activityType(request.getActivityType())
                .startDateTime(request.getStartDateTime())
                .endDateTime(request.getEndDateTime())
                .location(request.getLocation())
                .notes(request.getNotes())
                .build();
    }

    private ActivityResponse toResponse(Activity activity) {
        return new ActivityResponse(
                activity.getId(),
                activity.getDoctorId(),
                activity.getActivityType(),
                activity.getStartDateTime(),
                activity.getEndDateTime(),
                activity.getDurationMinutes(),
                activity.getLocation(),
                activity.getNotes(),
                activity.getCreatedDate(),
                activity.getLastModifiedDate()
        );
    }
}
