import type { ActivityType } from '../types/timesheet'

interface ActivityTypeOption {
  value: ActivityType
  label: string
  colorToken: string
}

export const ACTIVITY_TYPE_OPTIONS: ActivityTypeOption[] = [
  { value: 'CLINIC_BLOCK', label: 'Clinic Block', colorToken: 'clinic' },
  { value: 'SURGERY_BLOCK', label: 'Surgery Block', colorToken: 'surgery' },
  { value: 'ON_CALL', label: 'On-Call', colorToken: 'oncall' },
  { value: 'ON_SITE_ON_CALL', label: 'Onsite On-Call', colorToken: 'onsite-oncall' },
]
