package com.wardlog.timesheetservice.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.UUID;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CloseMonthRequest {

    // WORKAROUND: doctorId is accepted in the payload for now. In the real implementation
    // this must be derived from the auth token, not trusted from the request body.
    @NotNull
    private UUID doctorId;

    @NotNull
    private Integer year;

    @NotNull
    @Min(1)
    @Max(12)
    private Integer month;
}
