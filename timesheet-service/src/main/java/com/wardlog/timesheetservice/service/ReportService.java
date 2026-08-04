package com.wardlog.timesheetservice.service;

import com.wardlog.timesheetservice.dto.ActivityComparisonResponse;
import com.wardlog.timesheetservice.dto.ActivityResponse;
import com.wardlog.timesheetservice.dto.ActivityTrendsResponse;
import com.wardlog.timesheetservice.dto.ActivityTypeBreakdown;
import com.wardlog.timesheetservice.dto.BreakdownTrendResponse;
import com.wardlog.timesheetservice.dto.GapEntry;
import com.wardlog.timesheetservice.dto.GapHistoryEntry;
import com.wardlog.timesheetservice.dto.GapsReportResponse;
import com.wardlog.timesheetservice.dto.MonthlyTrend;
import com.wardlog.timesheetservice.dto.TrendBucket;
import com.wardlog.timesheetservice.dto.TrendTypeBreakdown;
import com.wardlog.timesheetservice.entity.Activity;
import com.wardlog.timesheetservice.enums.ActivityType;
import com.wardlog.timesheetservice.repository.ActivityRepository;
import com.wardlog.timesheetservice.repository.projection.ActivityTypeAggregate;
import com.wardlog.timesheetservice.repository.projection.MonthlyActivityTypeAggregate;
import com.wardlog.timesheetservice.util.PeriodResolver;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.YearMonth;
import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.HashMap;
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

    // WORKAROUND: no doctorId parameter for now. Once auth is wired up, this report
    // must be scoped to the doctor derived from the token.
    public GapsReportResponse gapsReport(LocalDate from, LocalDate to) {
        YearMonth anchorMonth = PeriodResolver.dominantMonth(from, to);
        List<YearMonth> lookbackMonths = List.of(
                anchorMonth.minusMonths(1),
                anchorMonth.minusMonths(2),
                anchorMonth.minusMonths(3));

        YearMonth earliestLookback = lookbackMonths.get(lookbackMonths.size() - 1);

        LocalDate queryStart = earliestLookback.atDay(1).isBefore(from) ? earliestLookback.atDay(1) : from;
        LocalDate queryEnd = to;

        LocalDateTime lower = queryStart.atStartOfDay();
        LocalDateTime upper = queryEnd.plusDays(1).atStartOfDay();

        List<Activity> activities = activityRepository.findByStartDateTimeRange(lower, upper);

        Map<LocalDate, List<Activity>> byDate = new HashMap<>();
        for (Activity activity : activities) {
            byDate.computeIfAbsent(activity.getStartDateTime().toLocalDate(), d -> new ArrayList<>())
                    .add(activity);
        }

        List<GapEntry> gaps = new ArrayList<>();
        for (LocalDate date = from; !date.isAfter(to); date = date.plusDays(1)) {
            if (byDate.containsKey(date)) {
                continue;
            }

            List<GapHistoryEntry> history = new ArrayList<>();
            int dayOfMonth = date.getDayOfMonth();

            for (YearMonth lookbackMonth : lookbackMonths) {
                if (dayOfMonth > lookbackMonth.lengthOfMonth()) {
                    continue;
                }

                LocalDate lookbackDate = lookbackMonth.atDay(dayOfMonth);
                List<Activity> onLookbackDate = byDate.getOrDefault(lookbackDate, List.of());

                history.add(GapHistoryEntry.builder()
                        .date(lookbackDate)
                        .activities(onLookbackDate.stream().map(this::toResponse).toList())
                        .build());
            }

            gaps.add(GapEntry.builder()
                    .date(date)
                    .history(history)
                    .build());
        }

        return GapsReportResponse.builder()
                .from(from)
                .to(to)
                .anchorMonth(anchorMonth)
                .lookbackMonths(lookbackMonths)
                .gaps(gaps)
                .build();
    }

    // WORKAROUND: no doctorId parameter for now. Once auth is wired up, this report
    // must be scoped to the doctor derived from the token.
    public BreakdownTrendResponse breakdownTrend(LocalDate from, LocalDate to) {
        boolean singleBucket = PeriodResolver.isShorterThanAWeek(from, to);

        List<LocalDate[]> ranges = singleBucket
                ? Collections.singletonList(new LocalDate[] { from, to })
                : PeriodResolver.calendarWeeks(from, to);

        LocalDateTime lower = from.atStartOfDay();
        LocalDateTime upper = to.plusDays(1).atStartOfDay();
        List<Activity> activities = activityRepository.findByStartDateTimeRange(lower, upper);

        List<TrendBucket> buckets = new ArrayList<>();
        for (LocalDate[] range : ranges) {
            LocalDate bucketFrom = range[0];
            LocalDate bucketTo = range[1];

            Map<ActivityType, Long> minutesByType = new EnumMap<>(ActivityType.class);
            for (Activity activity : activities) {
                LocalDate activityDate = activity.getStartDateTime().toLocalDate();
                if (activityDate.isBefore(bucketFrom) || activityDate.isAfter(bucketTo)) {
                    continue;
                }
                long minutes = activity.getDurationMinutes() == null ? 0L : activity.getDurationMinutes();
                minutesByType.merge(activity.getActivityType(), minutes, Long::sum);
            }

            long bucketTotal = minutesByType.values().stream().mapToLong(Long::longValue).sum();

            List<TrendTypeBreakdown> breakdown = new ArrayList<>();
            for (ActivityType type : ActivityType.values()) {
                long minutes = minutesByType.getOrDefault(type, 0L);
                double percentage = bucketTotal == 0
                        ? 0.0
                        : Math.round((minutes * 1000.0) / bucketTotal) / 10.0;

                breakdown.add(TrendTypeBreakdown.builder()
                        .activityType(type)
                        .label(type.getLabel())
                        .totalMinutes(minutes)
                        .percentage(percentage)
                        .build());
            }

            buckets.add(TrendBucket.builder()
                    .from(bucketFrom)
                    .to(bucketTo)
                    .totalMinutes(bucketTotal)
                    .breakdown(breakdown)
                    .build());
        }

        return BreakdownTrendResponse.builder()
                .from(from)
                .to(to)
                .bucketed(!singleBucket)
                .buckets(buckets)
                .build();
    }

    // WORKAROUND: no doctorId parameter for now. Once auth is wired up, this report
    // must be scoped to the doctor derived from the token.
    public ActivityTrendsResponse activityTrends(LocalDate from, LocalDate to) {
        LocalDateTime lower = from.atStartOfDay();
        LocalDateTime upper = to.plusDays(1).atStartOfDay();

        List<MonthlyActivityTypeAggregate> aggregates = activityRepository.aggregateByMonthAndType(lower, upper);

        Map<String, Map<ActivityType, MonthlyActivityTypeAggregate>> byMonthAndType = new HashMap<>();
        for (MonthlyActivityTypeAggregate aggregate : aggregates) {
            byMonthAndType.computeIfAbsent(aggregate.getMonth(), m -> new EnumMap<>(ActivityType.class))
                    .put(aggregate.getActivityType(), aggregate);
        }

        List<MonthlyTrend> months = new ArrayList<>();
        for (YearMonth yearMonth = YearMonth.from(from); !yearMonth.isAfter(YearMonth.from(to));
                yearMonth = yearMonth.plusMonths(1)) {
            String monthKey = yearMonth.toString();
            Map<ActivityType, MonthlyActivityTypeAggregate> byType =
                    byMonthAndType.getOrDefault(monthKey, Collections.emptyMap());

            List<ActivityTypeBreakdown> breakdown = new ArrayList<>();
            for (ActivityType type : ActivityType.values()) {
                MonthlyActivityTypeAggregate aggregate = byType.get(type);
                breakdown.add(ActivityTypeBreakdown.builder()
                        .activityType(type)
                        .label(type.getLabel())
                        .activityCount(aggregate == null ? 0L : aggregate.getActivityCount())
                        .totalMinutes(aggregate == null ? 0L : aggregate.getTotalMinutes())
                        .build());
            }

            months.add(MonthlyTrend.builder()
                    .month(monthKey)
                    .breakdown(breakdown)
                    .build());
        }

        return ActivityTrendsResponse.builder()
                .months(months)
                .build();
    }

    private ActivityResponse toResponse(Activity activity) {
        return new ActivityResponse(
                activity.getId(),
                activity.getDoctorId(),
                activity.getActivityType(),
                activity.getStartDateTime(),
                activity.getEndDateTime(),
                activity.getDurationMinutes(),
                activity.getLocation(),
                activity.getNotes(),
                activity.getCreatedDate(),
                activity.getLastModifiedDate()
        );
    }
}
