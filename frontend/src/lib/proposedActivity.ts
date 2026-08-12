import { ACTIVITY_TYPE_OPTIONS } from './activityType'

export const PROPOSED_ACTIVITY_TYPE_OPTIONS = ACTIVITY_TYPE_OPTIONS.map((option) => ({
  value: option.value,
  label: option.label,
}))

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
  const normalized = rawType.toLowerCase()
  const option = ACTIVITY_TYPE_OPTIONS.find((o) => o.value === normalized)
  if (!option) {
    return { label: rawType, ...UNKNOWN_TYPE_STYLE }
  }

  return { label: option.label, border: option.border, bg: option.bg, text: option.text, chipBg: option.chipBg }
}

export function isKnownProposedActivityType(rawType: string): boolean {
  return ACTIVITY_TYPE_OPTIONS.some((o) => o.value === rawType.toLowerCase())
}
