package com.wardlog.timesheetservice.dto;

import java.time.Instant;
import java.util.UUID;

public record DocumentResponse(

        UUID id,

        String fileName,

        String s3Key,

        String url,

        String contentType,

        Long fileSizeBytes,

        Instant createdDate
) {
}
