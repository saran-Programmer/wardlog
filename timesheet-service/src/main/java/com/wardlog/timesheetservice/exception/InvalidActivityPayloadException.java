package com.wardlog.timesheetservice.exception;

public class InvalidActivityPayloadException extends RuntimeException {

    public InvalidActivityPayloadException(String message) {
        super(message);
    }
}
