import { apiRequest } from './client'
import type { ActivityResponse, CreateActivityRequest } from '../types/timesheet'

export function createActivity(request: CreateActivityRequest): Promise<ActivityResponse> {
  return apiRequest<ActivityResponse>('/api/v1/activities', {
    method: 'POST',
    body: request,
  })
}
