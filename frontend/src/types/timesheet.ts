export type ActivityType = 'CLINIC_BLOCK' | 'SURGERY_BLOCK' | 'ON_CALL' | 'ON_SITE_ON_CALL'

export interface CreateActivityRequest {
  activityType: ActivityType
  startDateTime: string
  endDateTime: string
  location?: string
  notes?: string
}

export interface ActivityDocument {
  id: string
  fileName: string
  fileSizeBytes: number
  contentType?: string
}

// Mirrors AI-service's PatientSummary (graph/models/patient_details.py) — sourced from the
// Neo4j knowledge graph, not timesheet-service. No REST endpoint serves this yet.
export interface PatientSummary {
  name: string | null
  age: number | null
  sex: string | null
}

// Mirrors AI-service's ActivityConsultationSummary (graph/models/activity_details.py).
export interface ActivityConsultationSummary {
  patient: PatientSummary | null
  diagnoses: string[]
  drugs: string[]
  surgery_type: string | null
}

export interface ActivityResponse {
  id: string
  doctorId: string
  activityType: ActivityType
  startDateTime: string
  endDateTime: string
  durationMinutes: number
  location: string | null
  notes: string | null
  createdDate: string
  lastModifiedDate: string
  documents?: ActivityDocument[]
  consultations?: ActivityConsultationSummary[]
}
