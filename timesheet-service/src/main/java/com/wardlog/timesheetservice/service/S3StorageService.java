package com.wardlog.timesheetservice.service;

import com.wardlog.timesheetservice.config.AwsProperties;
import com.wardlog.timesheetservice.exception.FileStorageException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import software.amazon.awssdk.core.sync.RequestBody;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.Delete;
import software.amazon.awssdk.services.s3.model.DeleteObjectRequest;
import software.amazon.awssdk.services.s3.model.DeleteObjectsRequest;
import software.amazon.awssdk.services.s3.model.ObjectIdentifier;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
import software.amazon.awssdk.services.s3.model.S3Exception;

import java.io.IOException;
import java.util.Collection;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class S3StorageService {

    private final S3Client s3Client;
    private final AwsProperties awsProperties;

    /** Uploads under {@code keyPrefix}/{randomId}-{originalFileName} and returns the S3 key. */
    public String upload(String keyPrefix, MultipartFile file) {
        String key = keyPrefix + "/" + UUID.randomUUID() + "-" + file.getOriginalFilename();

        try {
            PutObjectRequest request = PutObjectRequest.builder()
                    .bucket(awsProperties.s3().bucket())
                    .key(key)
                    .contentType(file.getContentType())
                    .build();

            s3Client.putObject(request, RequestBody.fromInputStream(file.getInputStream(), file.getSize()));
        } catch (IOException | S3Exception e) {
            throw new FileStorageException("Failed to upload file to S3: " + file.getOriginalFilename(), e);
        }

        return key;
    }

    public void delete(String key) {
        try {
            s3Client.deleteObject(DeleteObjectRequest.builder()
                    .bucket(awsProperties.s3().bucket())
                    .key(key)
                    .build());
        } catch (S3Exception e) {
            throw new FileStorageException("Failed to delete file from S3: " + key, e);
        }
    }

    /** Batch delete via a single S3 DeleteObjects call. No-op for null/empty input. */
    public void deleteAll(Collection<String> keys) {
        if (keys == null || keys.isEmpty()) {
            return;
        }

        List<ObjectIdentifier> objectIds = keys.stream()
                .map(key -> ObjectIdentifier.builder().key(key).build())
                .toList();

        try {
            s3Client.deleteObjects(DeleteObjectsRequest.builder()
                    .bucket(awsProperties.s3().bucket())
                    .delete(Delete.builder().objects(objectIds).build())
                    .build());
        } catch (S3Exception e) {
            throw new FileStorageException("Failed to delete files from S3: " + keys, e);
        }
    }

    public String urlFor(String key) {
        return "https://%s.s3.%s.amazonaws.com/%s".formatted(
                awsProperties.s3().bucket(), awsProperties.region(), key);
    }
}
