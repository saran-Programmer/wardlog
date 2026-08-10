export type ActivityType = 'CLINIC_BLOCK' | 'SURGERY_BLOCK' | 'ON_CALL' | 'ON_SITE_ON_CALL'

export interface CreateActivityRequest {
  doctorId: string
  activityType: ActivityType
  startDateTime: string
  endDateTime: string
  location?: string
  notes?: string
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
}
