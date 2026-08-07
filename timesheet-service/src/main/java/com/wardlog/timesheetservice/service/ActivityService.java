package com.wardlog.timesheetservice.service;

import com.wardlog.timesheetservice.dto.ActivityListResponse;
import com.wardlog.timesheetservice.dto.ActivityMetaResponse;
import com.wardlog.timesheetservice.dto.ActivityResponse;
import com.wardlog.timesheetservice.dto.CreateActivityRequest;
import com.wardlog.timesheetservice.dto.DocumentResponse;
import com.wardlog.timesheetservice.dto.UpdateActivityRequest;
import com.wardlog.timesheetservice.entity.Activity;
import com.wardlog.timesheetservice.entity.Document;
import com.wardlog.timesheetservice.entity.Patient;
import com.wardlog.timesheetservice.enums.ActivityType;
import com.wardlog.timesheetservice.exception.ActivityNotFoundException;
import com.wardlog.timesheetservice.exception.ActivityOverlapException;
import com.wardlog.timesheetservice.messaging.ActivityEventPublisher;
import com.wardlog.timesheetservice.repository.ActivityRepository;
import jakarta.persistence.criteria.Predicate;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

import org.hibernate.Hibernate;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class ActivityService {

    private final ActivityRepository activityRepository;
    private final TimesheetClosureService timesheetClosureService;
    private final S3StorageService s3StorageService;
    private final ActivityEventPublisher activityEventPublisher;

    public ActivityResponse createActivity(CreateActivityRequest request, UUID doctorId, List<MultipartFile> files) {
        Activity activity = toEntity(request, doctorId);

        // Closed-month enforcement point: an activity belongs to the month of its
        // startDateTime only. Edit/delete will reuse this same guard when built.
        timesheetClosureService.assertMonthOpenForActivity(doctorId, request.getStartDateTime());

        if (activityRepository.existsOverlappingActivity(
                doctorId, request.getStartDateTime(), request.getEndDateTime(), null)) {
            throw new ActivityOverlapException(
                    "Activity overlaps with an existing activity for this doctor");
        }

        addDocuments(activity, files);

        Activity saved = activityRepository.save(activity);
        activityEventPublisher.publishActivityCreated(saved);
        return toResponse(saved);
    }

    /**
     * Attaches patient details (from the AI Service's patient event) to an already-persisted
     * activity. Logs and returns if the activity isn't found — the caller is a Kafka listener
     * and must not throw on a missing activity.
     */
    public void attachPatient(UUID activityId, Patient patient) {
        Activity activity = activityRepository.findById(activityId).orElse(null);
        if (activity == null) {
            log.error("Received patient event for unknown activity {}", activityId);
            return;
        }

        activity.setPatient(patient);
        activityRepository.save(activity);
    }

    public ActivityResponse getActivityById(UUID activityId) {
        Activity activity = activityRepository.findByIdWithDocuments(activityId)
                .orElseThrow(() -> new ActivityNotFoundException("Activity not found: " + activityId));
        return toResponse(activity);
    }

    public ActivityResponse updateActivity(UUID activityId, UpdateActivityRequest request,
                                            List<MultipartFile> newFiles, List<UUID> removeDocumentIds) {
        Activity existing = activityRepository.findByIdWithDocuments(activityId)
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

        removeDocuments(existing, removeDocumentIds);
        addDocuments(existing, newFiles);

        Activity saved = activityRepository.save(existing);
        activityEventPublisher.publishActivityUpdated(saved);
        return toResponse(saved);
    }

    public void deleteActivity(UUID activityId) {
        Activity activity = activityRepository.findByIdWithDocuments(activityId)
                .orElseThrow(() -> new ActivityNotFoundException("Activity not found: " + activityId));

        s3StorageService.deleteAll(activity.getDocuments().stream().map(Document::getS3Key).toList());

        activityRepository.deleteById(activityId);
        activityEventPublisher.publishActivityDeleted(activity);
    }

    /** Uploads each file to S3 under the activity's prefix and attaches it as a new Document. */
    private void addDocuments(Activity activity, List<MultipartFile> files) {
        if (files == null) {
            return;
        }
        for (MultipartFile file : files) {
            String key = s3StorageService.upload("activities/" + activity.getId(), file);

            activity.getDocuments().add(Document.builder()
                    .fileName(file.getOriginalFilename())
                    .s3Key(key)
                    .contentType(file.getContentType())
                    .fileSizeBytes(file.getSize())
                    .activity(activity)
                    .build());
        }
    }

    /** Deletes the matching documents from S3 and detaches them (orphanRemoval deletes the rows on save). */
    private void removeDocuments(Activity activity, List<UUID> removeDocumentIds) {
        if (removeDocumentIds == null || removeDocumentIds.isEmpty()) {
            return;
        }

        List<Document> toRemove = activity.getDocuments().stream()
                .filter(document -> removeDocumentIds.contains(document.getId()))
                .toList();

        s3StorageService.deleteAll(toRemove.stream().map(Document::getS3Key).toList());
        activity.getDocuments().removeAll(toRemove);
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

    private Activity toEntity(CreateActivityRequest request, UUID doctorId) {
        // Assigned here (rather than left to Activity's @PrePersist) so the id is
        // available up front to build S3 keys before the entity is saved.
        UUID id = request.getId() != null ? request.getId() : UUID.randomUUID();

        return Activity.builder()
                .id(id)
                .doctorId(doctorId)
                .activityType(request.getActivityType())
                .startDateTime(request.getStartDateTime())
                .endDateTime(request.getEndDateTime())
                .location(request.getLocation())
                .notes(request.getNotes())
                .build();
    }

    private ActivityResponse toResponse(Activity activity) {
        // documents is LAZY; only map it when already initialized (detail/create/update
        // paths fetch or populate it) so list views never trigger a load.
        List<DocumentResponse> documents = Hibernate.isInitialized(activity.getDocuments())
                ? activity.getDocuments().stream().map(this::toDocumentResponse).toList()
                : List.of();

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
                activity.getLastModifiedDate(),
                documents
        );
    }

    private DocumentResponse toDocumentResponse(Document document) {
        return new DocumentResponse(
                document.getId(),
                document.getFileName(),
                document.getS3Key(),
                s3StorageService.urlFor(document.getS3Key()),
                document.getContentType(),
                document.getFileSizeBytes(),
                document.getCreatedDate()
        );
    }
}
