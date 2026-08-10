import { apiRequest } from './client'
import { toDateInputValue } from '../lib/date'
import type { ActivityComparisonResponse } from '../types/timesheet'

export function getActivityComparison(from: Date, to: Date): Promise<ActivityComparisonResponse> {
  return apiRequest<ActivityComparisonResponse>('/api/v1/reports/activity-comparison', {
    params: { from: toDateInputValue(from), to: toDateInputValue(to) },
  })
}
