package com.wardlog.timesheetservice.enums;

public enum ActivityType {

    CLINIC_BLOCK("clinic block"),
    ON_CALL("on call"),
    ON_SITE_ON_CALL("on site on call"),
    SURGERY_BLOCK("surgery block");

    private final String label;

    ActivityType(String label) {
        this.label = label;
    }

    public String getLabel() {
        return label;
    }
}
