package com.wardlog.timesheetservice.dev;

import com.wardlog.timesheetservice.entity.Activity;
import com.wardlog.timesheetservice.enums.ActivityType;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * DEVELOPMENT-ONLY sample data for exercising activity/report endpoints without hand
 * seeding the database.
 *
 * A fixed 9-activity-per-month template is replayed across several months so the data
 * set covers different dates and months without hand-writing each entry; endDateTime is
 * always derived from startDateTime + durationMinutes, so the two can never disagree.
 */
public class SampleActivities {

    private static final UUID DOCTOR_ID = UUID.fromString("11111111-1111-1111-1111-111111111111");
    private static final int YEAR = 2026;
    private static final int[] MONTHS = {3, 4, 5, 6, 7, 8};

    private record Template(int day, int hour, int minute, long durationMinutes,
                             ActivityType type, String location, String notes) {
    }

    // Day 3 and day 16 each appear twice within a month, so day-level grouping has
    // multiple activities to group. All four activity types are represented.
    private static final List<Template> MONTH_TEMPLATE = List.of(
            new Template(3, 8, 0, 240, ActivityType.CLINIC_BLOCK, "Main Clinic", null),
            new Template(3, 19, 0, 660, ActivityType.ON_CALL, null, "Quiet shift"),
            new Template(6, 9, 0, 270, ActivityType.SURGERY_BLOCK, "OT 2", "Scheduled procedure"),
            new Template(9, 20, 0, 720, ActivityType.ON_SITE_ON_CALL, "Ward 4", null),
            new Template(12, 8, 0, 180, ActivityType.CLINIC_BLOCK, null, null),
            new Template(16, 17, 0, 240, ActivityType.ON_CALL, null, "Covered ER overflow"),
            new Template(16, 8, 0, 240, ActivityType.CLINIC_BLOCK, "Main Clinic", null),
            new Template(21, 7, 30, 150, ActivityType.SURGERY_BLOCK, "OT 1", null),
            new Template(25, 8, 0, 300, ActivityType.CLINIC_BLOCK, "Main Clinic", "Follow-up heavy day")
    );

    public static List<Activity> get() {
        List<Activity> activities = new ArrayList<>();
        int idIndex = 1;
        for (int month : MONTHS) {
            for (Template t : MONTH_TEMPLATE) {
                LocalDateTime start = LocalDateTime.of(YEAR, month, t.day(), t.hour(), t.minute());
                activities.add(Activity.builder()
                        .id(idFor(idIndex++))
                        .doctorId(DOCTOR_ID)
                        .activityType(t.type())
                        .startDateTime(start)
                        .endDateTime(start.plusMinutes(t.durationMinutes()))
                        .durationMinutes(t.durationMinutes())
                        .location(t.location())
                        .notes(t.notes())
                        .build());
            }
        }
        return List.copyOf(activities);
    }

    private static UUID idFor(int index) {
        return UUID.fromString(String.format("a1111111-0000-0000-0000-%012d", index));
    }
}
