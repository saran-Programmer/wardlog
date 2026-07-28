package com.wardlog.timesheetservice.dto;

import java.util.List;

public record ActivityListResponse(

        List<ActivityResponse> activities,

        ActivityMetaResponse meta
) {
}
