package com.wardlog.timesheetservice.messaging;

import com.wardlog.timesheetservice.dto.ActivityEvent;
import com.wardlog.timesheetservice.entity.Activity;
import com.wardlog.timesheetservice.enums.ActivityEventType;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
public class ActivityEventPublisher {

    private static final String TOPIC = "timesheet-to-ai-activity";

    private final KafkaTemplate<String, Object> kafkaTemplate;

    public void publishActivityCreated(Activity activity) {
        publish(ActivityEventType.CREATED, activity);
    }

    public void publishActivityUpdated(Activity activity) {
        publish(ActivityEventType.UPDATED, activity);
    }

    public void publishActivityDeleted(Activity activity) {
        publish(ActivityEventType.DELETED, activity);
    }

    /**
     * Fire-and-forget: failures are logged, never thrown, so a broker outage can't roll
     * back or block the DB operation that already succeeded.
     */
    private void publish(ActivityEventType eventType, Activity activity) {
        ActivityEvent event = new ActivityEvent(
                eventType,
                activity.getId(),
                activity.getDoctorId(),
                activity.getActivityType(),
                activity.getStartDateTime(),
                activity.getEndDateTime(),
                activity.getLocation(),
                activity.getNotes()
        );

        // Key = activityId so activity and patient events for the same activity land on
        // the same partition and are consumed in order.
        String key = activity.getId().toString();

        kafkaTemplate.send(TOPIC, key, event).whenComplete((result, ex) -> {
            if (ex != null) {
                log.error("Activity {} {} in DB but Kafka publish failed", activity.getId(), eventType, ex);
            }
        });
    }
}
