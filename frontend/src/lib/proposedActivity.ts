import { getActivityTypeOption } from './activityType'
import type { ActivityType } from '../types/timesheet'

const KNOWN_TYPES: { raw: string; activityType: ActivityType }[] = [
  { raw: 'clinicblock', activityType: 'CLINIC_BLOCK' },
  { raw: 'surgeryblock', activityType: 'SURGERY_BLOCK' },
  { raw: 'oncall', activityType: 'ON_CALL' },
  { raw: 'onsiteoncall', activityType: 'ON_SITE_ON_CALL' },
]

export const PROPOSED_ACTIVITY_TYPE_OPTIONS = KNOWN_TYPES.map(({ raw, activityType }) => {
  const option = getActivityTypeOption(activityType)
  return { value: raw, label: option.label }
})

interface ProposedActivityTypeStyle {
  label: string
  border: string
  bg: string
  text: string
  chipBg: string
}

const UNKNOWN_TYPE_STYLE: Omit<ProposedActivityTypeStyle, 'label'> = {
  border: 'border-white/10',
  bg: 'bg-white/5',
  text: 'text-text-muted',
  chipBg: 'bg-white/20',
}

export function describeProposedActivityType(rawType: string): ProposedActivityTypeStyle {
  const match = KNOWN_TYPES.find((t) => t.raw === rawType.toLowerCase())
  if (!match) {
    return { label: rawType, ...UNKNOWN_TYPE_STYLE }
  }

  const option = getActivityTypeOption(match.activityType)
  return {
    label: option.label,
    border: option.border,
    bg: option.bg,
    text: option.text,
    chipBg: option.chipBg,
  }
}

export function isKnownProposedActivityType(rawType: string): boolean {
  return KNOWN_TYPES.some((t) => t.raw === rawType.toLowerCase())
}
