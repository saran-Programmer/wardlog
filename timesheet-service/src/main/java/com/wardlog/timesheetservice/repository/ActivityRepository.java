package com.wardlog.timesheetservice.repository;

import com.wardlog.timesheetservice.entity.Activity;
import com.wardlog.timesheetservice.repository.projection.ActivityTypeAggregate;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface ActivityRepository extends JpaRepository<Activity, UUID>, JpaSpecificationExecutor<Activity> {

    /**
     * Loads an activity together with its documents in a single query. LEFT JOIN FETCH
     * so an activity with zero documents is still returned.
     */
    @Query("SELECT a FROM Activity a LEFT JOIN FETCH a.documents WHERE a.id = :id")
    Optional<Activity> findByIdWithDocuments(@Param("id") UUID id);

    /**
     * True if the doctor already has an activity whose [start, end) interval intersects
     * the given [start, end) interval. existing.start < end AND existing.end > start is
     * the general interval-overlap test — it covers containment either way, partial
     * overlap on either side, and identical ranges. Back-to-back activities (one ending
     * exactly when the other starts) are not considered an overlap. Pass excludingId as
     * null on create; pass the activity's own id on update so it doesn't overlap itself.
     */
    @Query("SELECT COUNT(a) > 0 FROM Activity a " +
            "WHERE a.doctorId = :doctorId " +
            "AND a.startDateTime < :endDateTime " +
            "AND a.endDateTime > :startDateTime " +
            "AND (:excludingId IS NULL OR a.id <> :excludingId)")
    boolean existsOverlappingActivity(@Param("doctorId") UUID doctorId,
                                       @Param("startDateTime") LocalDateTime startDateTime,
                                       @Param("endDateTime") LocalDateTime endDateTime,
                                       @Param("excludingId") UUID excludingId);

    /**
     * Per-activity-type counts and minute totals within [lower, upper), filtered on
     * startDateTime only — an activity belongs to the day it starts on. Returns rows
     * only for types with at least one activity in range; callers fill in the rest.
     */
    @Query("""
        SELECT a.activityType AS activityType,
               COUNT(a) AS activityCount,
               COALESCE(SUM(a.durationMinutes), 0) AS totalMinutes
        FROM Activity a
        WHERE a.startDateTime >= :lower AND a.startDateTime < :upper
        GROUP BY a.activityType
        """)
    List<ActivityTypeAggregate> aggregateByActivityType(@Param("lower") LocalDateTime lower,
                                                          @Param("upper") LocalDateTime upper);
}
