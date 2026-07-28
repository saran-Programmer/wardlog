package com.wardlog.timesheetservice.exception;

public class ActivityOverlapException extends RuntimeException {

    public ActivityOverlapException(String message) {
        super(message);
    }
}
