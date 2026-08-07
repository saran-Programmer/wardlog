package com.wardlog.timesheetservice.messaging;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.wardlog.timesheetservice.dto.CreateActivityRequest;
import com.wardlog.timesheetservice.dto.PatientEvent;
import com.wardlog.timesheetservice.entity.Patient;
import com.wardlog.timesheetservice.service.ActivityService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

/**
 * Consumes activity and patient events published by the AI Service. Each listener
 * traps its own exceptions so one bad message can't kill the consumer loop.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class AiActivityEventListener {

    private final ActivityService activityService;
    private final ObjectMapper kafkaConsumerObjectMapper;

    @KafkaListener(
            topics = "ai-to-timesheet-activity",
            groupId = "timesheet-service-ai-activity",
            containerFactory = "kafkaListenerContainerFactory")
    public void onActivityEvent(String message) {
        try {
            CreateActivityRequest request = kafkaConsumerObjectMapper.readValue(message, CreateActivityRequest.class);
            log.info("Consumed ai-to-timesheet-activity message for activityId={}", request.getId());

            activityService.createActivity(request, null);
            log.info("Persisted activity {} from AI Service event", request.getId());
        } catch (Exception ex) {
            log.error("Failed to process ai-to-timesheet-activity message: {}", message, ex);
        }
    }

    @KafkaListener(
            topics = "ai-to-timesheet-patient",
            groupId = "timesheet-service-ai-patient",
            containerFactory = "kafkaListenerContainerFactory")
    public void onPatientEvent(String message) {
        try {
            PatientEvent event = kafkaConsumerObjectMapper.readValue(message, PatientEvent.class);
            log.info("Consumed ai-to-timesheet-patient message for activityId={}", event.activityId());

            Patient patient = toPatient(event.patient());
            activityService.attachPatient(event.activityId(), patient);
            log.info("Attached patient details to activity {}", event.activityId());
        } catch (Exception ex) {
            log.error("Failed to process ai-to-timesheet-patient message: {}", message, ex);
        }
    }

    private Patient toPatient(PatientEvent.PatientPayload payload) {
        return Patient.builder()
                .name(payload.name())
                .age(payload.age())
                .sex(payload.sex())
                .diagnosis(payload.diagnosis())
                .drugs(payload.drugs())
                .build();
    }
}
