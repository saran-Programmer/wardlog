package com.wardlog.timesheetservice.service;

import com.wardlog.timesheetservice.dto.ActivityComparisonResponse;
import com.wardlog.timesheetservice.dto.ActivityTypeBreakdown;
import com.wardlog.timesheetservice.enums.ActivityType;
import com.wardlog.timesheetservice.repository.ActivityRepository;
import com.wardlog.timesheetservice.repository.projection.ActivityTypeAggregate;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class ReportService {

    private final ActivityRepository activityRepository;

    // WORKAROUND: no doctorId parameter for now. Once auth is wired up, this report
    // must be scoped to the doctor derived from the token.
    public ActivityComparisonResponse activityComparison(LocalDate from, LocalDate to) {
        LocalDateTime lower = from.atStartOfDay();
        LocalDateTime upper = to.plusDays(1).atStartOfDay();

        List<ActivityTypeAggregate> aggregates = activityRepository.aggregateByActivityType(lower, upper);

        Map<ActivityType, ActivityTypeAggregate> byType = new EnumMap<>(ActivityType.class);
        for (ActivityTypeAggregate aggregate : aggregates) {
            byType.put(aggregate.getActivityType(), aggregate);
        }

        List<ActivityTypeBreakdown> breakdown = new ArrayList<>();
        for (ActivityType type : ActivityType.values()) {
            ActivityTypeAggregate aggregate = byType.get(type);
            breakdown.add(ActivityTypeBreakdown.builder()
                    .activityType(type)
                    .label(type.getLabel())
                    .activityCount(aggregate == null ? 0L : aggregate.getActivityCount())
                    .totalMinutes(aggregate == null ? 0L : aggregate.getTotalMinutes())
                    .build());
        }

        return ActivityComparisonResponse.builder()
                .from(from)
                .to(to)
                .breakdown(breakdown)
                .build();
    }
}
