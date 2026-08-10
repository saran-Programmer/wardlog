import { useEffect, useState } from 'react'
import { getActivities } from '../../../api/activities'
import { ApiError } from '../../../api/client'
import { ACTIVITY_TYPE_OPTIONS, getActivityTypeOption } from '../../../lib/activityType'
import { formatHours, toDateInputValue } from '../../../lib/date'
import type { ActivityMetaResponse, ActivityResponse, ActivityType } from '../../../types/timesheet'

const dayHeaderFormat = new Intl.DateTimeFormat('en-US', { weekday: 'long', month: 'short', day: 'numeric' })
const timeFormat = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit' })

const EMPTY_META: ActivityMetaResponse = {
  clinicBlockMinutes: 0,
  surgeryBlockMinutes: 0,
  onCallMinutes: 0,
  onSiteOnCallMinutes: 0,
}

function minutesForType(type: ActivityType, meta: ActivityMetaResponse): number {
  switch (type) {
    case 'CLINIC_BLOCK':
      return meta.clinicBlockMinutes
    case 'SURGERY_BLOCK':
      return meta.surgeryBlockMinutes
    case 'ON_CALL':
      return meta.onCallMinutes
    case 'ON_SITE_ON_CALL':
      return meta.onSiteOnCallMinutes
  }
}

interface MonthCloseTabProps {
  monthDate: Date
}

export function MonthCloseTab({ monthDate }: MonthCloseTabProps) {
  const year = monthDate.getFullYear()
  const month = monthDate.getMonth()
  const daysInMonth = new Date(year, month + 1, 0).getDate()

  const [activities, setActivities] = useState<ActivityResponse[]>([])
  const [meta, setMeta] = useState<ActivityMetaResponse>(EMPTY_META)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setIsLoading(true)
    setLoadError(null)
    const startDate = toDateInputValue(new Date(year, month, 1))
    const endDate = toDateInputValue(new Date(year, month, daysInMonth))

    getActivities(startDate, endDate)
      .then((activityList) => {
        if (cancelled) return
        setActivities(activityList.activities)
        setMeta(activityList.meta)
      })
      .catch((err) => {
        if (!cancelled) setLoadError(err instanceof ApiError ? err.message : 'Unable to load this month.')
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [year, month, daysInMonth])

  const totalMinutes =
    meta.clinicBlockMinutes + meta.surgeryBlockMinutes + meta.onCallMinutes + meta.onSiteOnCallMinutes

  const activitiesByDay = new Map<string, ActivityResponse[]>()
  activities.forEach((activity) => {
    const key = toDateInputValue(new Date(activity.startDateTime))
    const dayActivities = activitiesByDay.get(key) ?? []
    dayActivities.push(activity)
    activitiesByDay.set(key, dayActivities)
  })
  activitiesByDay.forEach((dayActivities) =>
    dayActivities.sort((a, b) => a.startDateTime.localeCompare(b.startDateTime)),
  )
  const sortedDayKeys = Array.from(activitiesByDay.keys()).sort((a, b) => b.localeCompare(a))

  return (
    <div className="calendar-scroll mt-4 min-h-0 flex-1 overflow-y-auto pr-1">
      {loadError && <p className="pb-4 text-sm text-red-400">{loadError}</p>}

      <div className="grid grid-cols-5 gap-4">
        <div className="rounded-2xl border border-white/5 bg-surface p-5">
          <p className="text-xs font-semibold uppercase tracking-wide text-text-subtle">Total Logged</p>
          <p className="mt-2 text-3xl font-bold text-accent-strong">{formatHours(totalMinutes)}</p>
        </div>

        {ACTIVITY_TYPE_OPTIONS.map((option) => {
          const minutes = minutesForType(option.value, meta)
          const pct = totalMinutes > 0 ? Math.min(100, (minutes / totalMinutes) * 100) : 0
          return (
            <div key={option.value} className="rounded-2xl border border-white/5 bg-surface p-5">
              <div className="flex items-center gap-2">
                <span className={`h-2 w-2 rounded-full ${option.chipBg}`} />
                <p className="text-sm text-text-muted">{option.label}</p>
              </div>
              <p className="mt-2 text-3xl font-bold text-text">{formatHours(minutes)}</p>
              <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-white/10">
                <div className={`h-full rounded-full ${option.chipBg}`} style={{ width: `${pct}%` }} />
              </div>
            </div>
          )
        })}
      </div>

      <div className="mt-8 pb-4">
        <h2 className="text-base font-semibold text-text">Activities this month</h2>

        {!isLoading && sortedDayKeys.length === 0 && (
          <p className="mt-4 text-sm text-text-muted">No activities logged this month.</p>
        )}

        <div className="mt-4 space-y-6">
          {sortedDayKeys.map((dayKey) => {
            const dayActivities = activitiesByDay.get(dayKey)!
            const dayMinutes = dayActivities.reduce((sum, activity) => sum + activity.durationMinutes, 0)
            const [dayYear, dayMonth, day] = dayKey.split('-').map(Number)

            return (
              <div key={dayKey}>
                <div className="flex items-center justify-between border-b border-white/10 pb-2">
                  <p className="text-sm font-semibold text-text">
                    {dayHeaderFormat.format(new Date(dayYear, dayMonth - 1, day))}
                  </p>
                  <p className="text-sm text-text-muted">{formatHours(dayMinutes)}</p>
                </div>

                <div className="mt-3 space-y-3">
                  {dayActivities.map((activity) => {
                    const option = getActivityTypeOption(activity.activityType)
                    const start = new Date(activity.startDateTime)
                    const end = new Date(activity.endDateTime)
                    return (
                      <div
                        key={activity.id}
                        className="flex items-center gap-4 rounded-xl border border-white/5 bg-surface-raised px-4 py-3"
                      >
                        <span
                          className={`shrink-0 rounded-full px-3 py-1 text-xs font-semibold ${option.bg} ${option.text}`}
                        >
                          {option.label}
                        </span>
                        <span className="shrink-0 text-sm text-text">
                          {timeFormat.format(start)} – {timeFormat.format(end)}
                        </span>
                        <span className="flex-1 truncate text-sm text-text-muted">{activity.location}</span>
                        <span className="shrink-0 text-sm text-text-muted">
                          {formatHours(activity.durationMinutes)}
                        </span>
                      </div>
                    )
                  })}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
