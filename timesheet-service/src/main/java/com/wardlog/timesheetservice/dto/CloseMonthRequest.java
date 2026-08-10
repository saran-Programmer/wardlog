package com.wardlog.timesheetservice.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CloseMonthRequest {

    @NotNull
    private Integer year;

    @NotNull
    @Min(1)
    @Max(12)
    private Integer month;
}
