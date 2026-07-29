package com.wardlog.timesheetservice.exception;

public class MonthAlreadyClosedException extends RuntimeException {

    public MonthAlreadyClosedException(String message) {
        super(message);
    }
}
