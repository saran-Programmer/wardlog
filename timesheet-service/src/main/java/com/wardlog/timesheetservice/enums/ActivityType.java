package com.wardlog.timesheetservice.enums;

public enum ActivityType {

    clinicblock("clinic block"),
    oncall("on call"),
    onsiteoncall("on site on call"),
    surgeryblock("surgery block");

    private final String label;

    ActivityType(String label) {
        this.label = label;
    }

    public String getLabel() {
        return label;
    }
}
