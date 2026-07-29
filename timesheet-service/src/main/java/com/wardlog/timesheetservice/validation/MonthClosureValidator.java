package com.wardlog.timesheetservice.validation;

import com.wardlog.timesheetservice.dto.CloseMonthRequest;
import com.wardlog.timesheetservice.exception.InvalidActivityPayloadException;
import org.springframework.stereotype.Component;

import java.time.YearMonth;

@Component
public class MonthClosureValidator {

    public void validateClose(CloseMonthRequest request) {
        Integer month = request.getMonth();
        Integer year = request.getYear();

        if (month != null && (month < 1 || month > 12)) {
            throw new InvalidActivityPayloadException("month must be between 1 and 12");
        }

        if (year != null && month != null) {
            YearMonth requested = YearMonth.of(year, month);
            if (requested.isAfter(YearMonth.now())) {
                throw new InvalidActivityPayloadException("cannot close a future month");
            }
        }
    }
}
