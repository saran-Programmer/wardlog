import { apiRequest } from './client'
import type {
  ActivityListResponse,
  ActivityResponse,
  CreateActivityRequest,
  UpdateActivityRequest,
} from '../types/timesheet'

export function createActivity(request: CreateActivityRequest): Promise<ActivityResponse> {
  const formData = new FormData()
  formData.append('activity', new Blob([JSON.stringify(request)], { type: 'application/json' }))

  return apiRequest<ActivityResponse>('/api/v1/activities', {
    method: 'POST',
    body: formData,
  })
}

export function getActivityById(activityId: string): Promise<ActivityResponse> {
  return apiRequest<ActivityResponse>(`/api/v1/activities/${activityId}`)
}

export function getActivities(startDate: string, endDate: string): Promise<ActivityListResponse> {
  return apiRequest<ActivityListResponse>('/api/v1/activities', {
    params: { startDate, endDate },
  })
}

export function updateActivity(activityId: string, request: UpdateActivityRequest): Promise<ActivityResponse> {
  const formData = new FormData()
  formData.append('activity', new Blob([JSON.stringify(request)], { type: 'application/json' }))

  return apiRequest<ActivityResponse>(`/api/v1/activities/${activityId}`, {
    method: 'PUT',
    body: formData,
  })
}

export function deleteActivity(activityId: string): Promise<void> {
  return apiRequest<void>(`/api/v1/activities/${activityId}`, {
    method: 'DELETE',
  })
}
