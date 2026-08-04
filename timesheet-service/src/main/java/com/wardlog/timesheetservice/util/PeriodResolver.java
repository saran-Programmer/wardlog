package com.wardlog.timesheetservice.util;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.YearMonth;
import java.time.temporal.ChronoUnit;
import java.time.temporal.TemporalAdjusters;
import java.util.ArrayList;
import java.util.List;

/**
 * Calendar/period math shared by report queries. Plain date utility — not a template
 * method hierarchy, since the reports that use it don't share an algorithm skeleton.
 */
public final class PeriodResolver {

    private PeriodResolver() {
    }

    /**
     * The calendar month with the most days inside [from, to]. Months are scanned in
     * chronological order and only a strictly greater day count replaces the current
     * winner, so ties resolve to the earlier month.
     */
    public static YearMonth dominantMonth(LocalDate from, LocalDate to) {
        YearMonth winner = null;
        int winnerDays = -1;

        YearMonth month = YearMonth.from(from);
        YearMonth lastMonth = YearMonth.from(to);

        while (!month.isAfter(lastMonth)) {
            LocalDate overlapStart = month.atDay(1).isAfter(from) ? month.atDay(1) : from;
            LocalDate overlapEnd = month.atEndOfMonth().isBefore(to) ? month.atEndOfMonth() : to;

            int days = (int) ChronoUnit.DAYS.between(overlapStart, overlapEnd) + 1;

            if (days > winnerDays) {
                winnerDays = days;
                winner = month;
            }

            month = month.plusMonths(1);
        }

        return winner;
    }

    /**
     * Splits [from, to] into ISO calendar weeks (Monday-Sunday). The first and last
     * entries are clipped to the range bounds.
     */
    public static List<LocalDate[]> calendarWeeks(LocalDate from, LocalDate to) {
        List<LocalDate[]> weeks = new ArrayList<>();

        LocalDate weekStart = from.with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY));

        while (!weekStart.isAfter(to)) {
            LocalDate weekEnd = weekStart.with(TemporalAdjusters.nextOrSame(DayOfWeek.SUNDAY));

            LocalDate clippedStart = weekStart.isBefore(from) ? from : weekStart;
            LocalDate clippedEnd = weekEnd.isAfter(to) ? to : weekEnd;

            weeks.add(new LocalDate[] { clippedStart, clippedEnd });

            weekStart = weekStart.plusWeeks(1);
        }

        return weeks;
    }

    /** True when the range spans fewer than 7 days, counting both endpoints. */
    public static boolean isShorterThanAWeek(LocalDate from, LocalDate to) {
        return ChronoUnit.DAYS.between(from, to) + 1 < 7;
    }
}
