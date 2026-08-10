import { apiRequest } from './client'
import type { CloseMonthRequest, MonthClosureResponse, MonthStatusResponse } from '../types/timesheet'

export function getMonthStatus(year: number, month: number): Promise<MonthStatusResponse> {
  return apiRequest<MonthStatusResponse>('/api/v1/timesheet/status', {
    params: { year: String(year), month: String(month) },
  })
}

export function closeMonth(request: CloseMonthRequest): Promise<MonthClosureResponse> {
  return apiRequest<MonthClosureResponse>('/api/v1/timesheet/close', { method: 'POST', body: request })
}
