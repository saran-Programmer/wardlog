package com.wardlog.userservice.enums;

public enum ToneType {

    WARM("warm"),
    FUNNY("funny"),
    PROFESSIONAL("professional");

    private final String label;

    ToneType(String label) {
        this.label = label;
    }

    public String getLabel() {
        return label;
    }
}
