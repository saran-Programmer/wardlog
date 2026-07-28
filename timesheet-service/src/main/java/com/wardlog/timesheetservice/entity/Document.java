package com.wardlog.timesheetservice.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EntityListeners;
import jakarta.persistence.FetchType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.Instant;
import java.util.UUID;

/**
 * Metadata for a single file attached to an {@link Activity} (e.g. a consent form or
 * pre-op imaging PDF). The actual file lives in S3; this row stores only its metadata.
 */
@Entity
@Table(name = "document")
@EntityListeners(AuditingEntityListener.class)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Document {

    /**
     * Primary key. May arrive pre-assigned (e.g. from the AI Service) or unset
     * (e.g. from a direct UI upload) — see {@link #assignIdIfAbsent()}, which fills it
     * in only when the caller left it null. No @GeneratedValue: generation is handled
     * in code, not delegated to the DB/Hibernate.
     */
    @Id
    @Column(name = "id")
    private UUID id;

    /** Original file name, e.g. "Webb_Consent_Form.pdf". */
    @Column(name = "file_name", nullable = false)
    private String fileName;

    /** The S3 object key used to fetch the file back. */
    @Column(name = "s3_key", nullable = false)
    private String s3Key;

    /** MIME type, e.g. "application/pdf". */
    @Column(name = "content_type", nullable = false)
    private String contentType;

    /** File size in bytes. UI displays this as KB/MB. */
    @Column(name = "file_size_bytes", nullable = false)
    private Long fileSizeBytes;

    /** Owning activity. Owning side of the FK. */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "activity_id", nullable = false)
    private Activity activity;

    /** Audit: when the row was first persisted. Immutable after creation. */
    @CreatedDate
    @Column(name = "created_date", updatable = false)
    private Instant createdDate;

    /** Audit: when the row was last modified. */
    @LastModifiedDate
    @Column(name = "last_modified_date")
    private Instant lastModifiedDate;

    @PrePersist
    private void assignIdIfAbsent() {
        if (id == null) id = UUID.randomUUID();
    }
}
