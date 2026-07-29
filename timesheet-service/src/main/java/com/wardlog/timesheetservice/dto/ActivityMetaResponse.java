package com.wardlog.timesheetservice.dto;

public record ActivityMetaResponse(

        Long clinicBlockMinutes,

        Long surgeryBlockMinutes,

        Long onCallMinutes,

        Long onSiteOnCallMinutes
) {
}
