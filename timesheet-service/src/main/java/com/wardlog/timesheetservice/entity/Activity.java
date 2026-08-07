package com.wardlog.timesheetservice.entity;

import com.wardlog.timesheetservice.enums.ActivityType;
import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Embedded;
import jakarta.persistence.Entity;
import jakarta.persistence.EntityListeners;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.PrePersist;
import jakarta.persistence.PreUpdate;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.Duration;
import java.time.Instant;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * A single logged unit of clinical work (clinic block, on-call, surgery, etc.).
 * Source of truth for the doctor's timesheet.
 */
@Entity
@Table(name = "activity")
@EntityListeners(AuditingEntityListener.class)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Activity {

    /**
     * Primary key. May arrive pre-assigned (e.g. from the AI Service) or unset
     * (e.g. from a direct UI flow) — see {@link #assignIdIfAbsent()}, which fills it
     * in only when the caller left it null. No @GeneratedValue: generation is handled
     * in code, not delegated to the DB/Hibernate.
     */
    @Id
    @Column(name = "id")
    private UUID id;

    /** Owning doctor. Supplied via the request payload; not a managed relationship. */
    @Column(name = "doctor_id", nullable = false)
    private UUID doctorId;

    /** Kind of activity block. Stored as the enum constant name, not the display label. */
    @Enumerated(EnumType.STRING)
    @Column(name = "activity_type", nullable = false)
    private ActivityType activityType;

    /** Start of the activity block. */
    @Column(name = "start_date_time", nullable = false)
    private LocalDateTime startDateTime;

    /** End of the activity block. */
    @Column(name = "end_date_time", nullable = false)
    private LocalDateTime endDateTime;

    /**
     * Duration in minutes. Persisted, but always derived from start/end at save time —
     * see {@link #computeDurationMinutes()}. Callers should not set this directly;
     * any value they pass is overwritten before insert/update.
     */
    @Column(name = "duration_minutes")
    private Long durationMinutes;

    /** Free-text notes for this activity. Optional; at most one per activity. */
    @Column(name = "notes")
    private String notes;

    /** Free-text location where the activity took place (e.g. ward, OT, clinic name). Optional. */
    @Column(name = "location")
    private String location;

    /** Audit: when the row was first persisted. Immutable after creation. */
    @CreatedDate
    @Column(name = "created_date", updatable = false)
    private Instant createdDate;

    /** Audit: when the row was last modified. */
    @LastModifiedDate
    @Column(name = "last_modified_date")
    private Instant lastModifiedDate;

    /**
     * Documents attached to this activity (consent forms, imaging, etc.). LAZY so list
     * views never load documents; fetched explicitly (see
     * {@code ActivityRepository#findByIdWithDocuments}) only on the detail view.
     */
    @OneToMany(mappedBy = "activity", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    @Builder.Default
    private List<Document> documents = new ArrayList<>();

    /**
     * Patient details for this activity's encounter. Null until the AI Service's
     * patient event arrives on "ai-to-timesheet-patient" and attaches it.
     */
    @Embedded
    private Patient patient;

    /**
     * JPA allows only one @PrePersist method per entity class, so id-assignment and
     * duration computation are both driven from here rather than annotated separately.
     */
    @PrePersist
    private void beforePersist() {
        
        if (id == null) id = UUID.randomUUID();
        
        computeDurationMinutes();
    }

    /**
     * Recomputes durationMinutes from startDateTime/endDateTime before every insert
     * and update, so the stored value can never drift from the caller-supplied times.
     */
    @PreUpdate
    private void computeDurationMinutes() {
        durationMinutes = Duration.between(startDateTime, endDateTime).toMinutes();
    }
}
