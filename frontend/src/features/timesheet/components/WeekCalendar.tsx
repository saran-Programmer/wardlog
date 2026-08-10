import { useEffect, useState, type CSSProperties } from 'react'
import { useUser } from '../../../hooks/useUser'
import { getActivities } from '../../../api/activities'
import { ApiError } from '../../../api/client'
import { dateAtMinutes, toDateInputValue } from '../../../lib/date'
import { TimeGrid, type TimeGridActivity } from './TimeGrid'
import { CreateActivityModal } from './CreateActivityModal'
import { ActivityDetailDrawer } from './ActivityDetailDrawer'
import type { ActivityResponse } from '../../../types/timesheet'

function isSameDate(a: Date, b: Date) {
  return a.getDate() === b.getDate() && a.getMonth() === b.getMonth() && a.getFullYear() === b.getFullYear()
}

const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

interface WeekCalendarProps {
  weekStart: Date
  direction: 1 | -1
}

interface PendingRange {
  start: Date
  end: Date
}

export function WeekCalendar({ weekStart, direction }: WeekCalendarProps) {
  const { user } = useUser()
  const today = new Date()

  const days = Array.from({ length: 7 }, (_, index) => {
    const date = new Date(weekStart)
    date.setDate(weekStart.getDate() + index)
    return date
  })

  function isToday(date: Date) {
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    )
  }

  const [pendingRange, setPendingRange] = useState<PendingRange | null>(null)
  const [activities, setActivities] = useState<ActivityResponse[]>([])
  const [selectedActivityId, setSelectedActivityId] = useState<string | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)

  const weekEnd = days[6]

  useEffect(() => {
    let cancelled = false
    setLoadError(null)
    const startDate = toDateInputValue(weekStart)
    const endDate = toDateInputValue(weekEnd)

    getActivities(startDate, endDate)
      .then((response) => {
        if (!cancelled) setActivities(response.activities)
      })
      .catch((err) => {
        if (!cancelled) setLoadError(err instanceof ApiError ? err.message : 'Unable to load activities.')
      })

    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [weekStart.getTime()])

  function handleSelectRange(columnIndex: number, startMinutes: number, endMinutes: number) {
    const day = days[columnIndex]
    setPendingRange({
      start: dateAtMinutes(day, startMinutes),
      end: dateAtMinutes(day, endMinutes),
    })
  }

  const gridActivities: TimeGridActivity[] = activities.flatMap((activity) => {
    const start = new Date(activity.startDateTime)
    const end = new Date(activity.endDateTime)
    const columnIndex = days.findIndex((day) => isSameDate(day, start))
    if (columnIndex === -1) return []

    return [
      {
        id: activity.id,
        columnIndex,
        startMinutes: start.getHours() * 60 + start.getMinutes(),
        endMinutes: isSameDate(start, end) ? end.getHours() * 60 + end.getMinutes() : 24 * 60,
        activityType: activity.activityType,
        location: activity.location,
      },
    ]
  })

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <p className="pb-3 text-sm text-text-subtle">Click an hour or drag across a range to log an activity.</p>
      {loadError && <p className="pb-3 text-sm text-red-400">{loadError}</p>}

      <div className="grid grid-cols-[56px_repeat(7,1fr)]">
        <div />
        {days.map((date) => (
          <div key={date.toISOString()} className="pb-2 text-center">
            <div className="text-sm font-medium text-text-muted">{WEEKDAYS[date.getDay()]}</div>
            <div
              className={`mx-auto mt-1 flex h-6 w-6 items-center justify-center rounded-full text-sm font-medium ${
                isToday(date) ? 'bg-accent text-bg' : 'text-text'
              }`}
            >
              {date.getDate()}
            </div>
          </div>
        ))}
      </div>

      <div
        key={weekStart.toISOString()}
        className="animate-calendar-slide flex min-h-0 flex-1 flex-col"
        style={{ '--slide-from': `${direction * 24}px` } as CSSProperties}
      >
        <TimeGrid
          columnCount={7}
          isColumnToday={(columnIndex) => isToday(days[columnIndex])}
          onSelectRange={handleSelectRange}
          activities={gridActivities}
          onSelectActivity={setSelectedActivityId}
        />
      </div>

      {pendingRange && user && (
        <CreateActivityModal
          start={pendingRange.start}
          end={pendingRange.end}
          onClose={() => setPendingRange(null)}
          onCreated={(activity) => {
            setActivities((prev) => [...prev, activity])
            setPendingRange(null)
          }}
        />
      )}

      {selectedActivityId && (
        <ActivityDetailDrawer activityId={selectedActivityId} onClose={() => setSelectedActivityId(null)} />
      )}
    </div>
  )
}
