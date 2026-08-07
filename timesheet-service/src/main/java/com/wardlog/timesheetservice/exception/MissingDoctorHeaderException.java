package com.wardlog.timesheetservice.exception;

public class MissingDoctorHeaderException extends RuntimeException {

    public MissingDoctorHeaderException(String message) {
        super(message);
    }
}
