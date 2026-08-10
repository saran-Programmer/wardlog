import type { ActivityType } from '../types/timesheet'

interface ActivityTypeOption {
  value: ActivityType
  label: string
  border: string
  bg: string
  text: string
  chipBg: string
}

export const ACTIVITY_TYPE_OPTIONS: ActivityTypeOption[] = [
  {
    value: 'CLINIC_BLOCK',
    label: 'Clinic Block',
    border: 'border-clinic',
    bg: 'bg-clinic-fill',
    text: 'text-clinic',
    chipBg: 'bg-clinic',
  },
  {
    value: 'SURGERY_BLOCK',
    label: 'Surgery Block',
    border: 'border-surgery',
    bg: 'bg-surgery-fill',
    text: 'text-surgery',
    chipBg: 'bg-surgery',
  },
  {
    value: 'ON_CALL',
    label: 'On-Call',
    border: 'border-oncall',
    bg: 'bg-oncall-fill',
    text: 'text-oncall',
    chipBg: 'bg-oncall',
  },
  {
    value: 'ON_SITE_ON_CALL',
    label: 'Onsite On-Call',
    border: 'border-onsite-oncall',
    bg: 'bg-onsite-oncall-fill',
    text: 'text-onsite-oncall',
    chipBg: 'bg-onsite-oncall',
  },
]

export function getActivityTypeOption(activityType: ActivityType): ActivityTypeOption {
  return ACTIVITY_TYPE_OPTIONS.find((option) => option.value === activityType)!
}
