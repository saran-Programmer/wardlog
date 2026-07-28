package com.wardlog.timesheetservice.validation;

import com.wardlog.timesheetservice.dto.CreateActivityRequest;
import com.wardlog.timesheetservice.dto.UpdateActivityRequest;
import com.wardlog.timesheetservice.exception.InvalidActivityPayloadException;
import org.springframework.stereotype.Component;


@Component
public class ActivityValidator {

    public void validateCreate(CreateActivityRequest request) {
        if (request.getStartDateTime() != null && request.getEndDateTime() != null
                && !request.getEndDateTime().isAfter(request.getStartDateTime())) {
            throw new InvalidActivityPayloadException("endDateTime must be after startDateTime");
        }
    }

    public void validateUpdate(UpdateActivityRequest request) {
        if (request.getStartDateTime() != null && request.getEndDateTime() != null
                && !request.getEndDateTime().isAfter(request.getStartDateTime())) {
            throw new InvalidActivityPayloadException("endDateTime must be after startDateTime");
        }
    }
}
