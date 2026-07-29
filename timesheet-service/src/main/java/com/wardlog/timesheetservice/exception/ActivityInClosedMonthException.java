package com.wardlog.timesheetservice.exception;

public class ActivityInClosedMonthException extends RuntimeException {

    public ActivityInClosedMonthException(String message) {
        super(message);
    }
}
