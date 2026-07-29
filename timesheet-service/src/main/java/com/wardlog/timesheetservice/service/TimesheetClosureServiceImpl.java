package com.wardlog.timesheetservice.service;

import com.wardlog.timesheetservice.dto.CloseMonthRequest;
import com.wardlog.timesheetservice.dto.MonthClosureResponse;
import com.wardlog.timesheetservice.dto.MonthStatusResponse;
import com.wardlog.timesheetservice.entity.MonthClosure;
import com.wardlog.timesheetservice.exception.ActivityInClosedMonthException;
import com.wardlog.timesheetservice.exception.MonthAlreadyClosedException;
import com.wardlog.timesheetservice.repository.MonthClosureRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.time.LocalDateTime;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class TimesheetClosureServiceImpl implements TimesheetClosureService {

    private final MonthClosureRepository monthClosureRepository;

    @Override
    public MonthClosureResponse closeMonth(CloseMonthRequest request) {
        UUID doctorId = request.getDoctorId();
        int year = request.getYear();
        int month = request.getMonth();

        if (monthClosureRepository.existsByDoctorIdAndYearAndMonth(doctorId, year, month)) {
            throw new MonthAlreadyClosedException("month already closed / submitted");
        }

        MonthClosure closure = MonthClosure.builder()
                .doctorId(doctorId)
                .year(year)
                .month(month)
                .closedAt(Instant.now())
                .build();

        MonthClosure saved = monthClosureRepository.save(closure);
        return toResponse(saved);
    }

    @Override
    public MonthStatusResponse getStatus(UUID doctorId, int year, int month) {
        return monthClosureRepository.findByDoctorIdAndYearAndMonth(doctorId, year, month)
                .map(closure -> new MonthStatusResponse(true, closure.getClosedAt()))
                .orElse(new MonthStatusResponse(false, null));
    }

    @Override
    public void assertMonthOpenForActivity(UUID doctorId, LocalDateTime activityStart) {
        int year = activityStart.getYear();
        int month = activityStart.getMonthValue();

        if (monthClosureRepository.existsByDoctorIdAndYearAndMonth(doctorId, year, month)) {
            throw new ActivityInClosedMonthException("cannot log an activity in a closed month");
        }
    }

    private MonthClosureResponse toResponse(MonthClosure closure) {
        return new MonthClosureResponse(
                closure.getId(),
                closure.getDoctorId(),
                closure.getYear(),
                closure.getMonth(),
                closure.getClosedAt()
        );
    }
}
