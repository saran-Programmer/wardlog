import { useEffect, useState, type CSSProperties } from 'react'
import { Loader2 } from 'lucide-react'
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

interface DayCalendarProps {
  date: Date
  direction: 1 | -1
}

interface PendingRange {
  start: Date
  end: Date
}

export function DayCalendar({ date, direction }: DayCalendarProps) {
  const { user } = useUser()
  const today = new Date()
  const isToday =
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()

  const [pendingRange, setPendingRange] = useState<PendingRange | null>(null)
  const [activities, setActivities] = useState<ActivityResponse[]>([])
  const [selectedActivityId, setSelectedActivityId] = useState<string | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setIsLoading(true)
    setLoadError(null)
    const isoDate = toDateInputValue(date)

    getActivities(isoDate, isoDate)
      .then((response) => {
        if (!cancelled) setActivities(response.activities)
      })
      .catch((err) => {
        if (!cancelled) setLoadError(err instanceof ApiError ? err.message : 'Unable to load activities.')
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false)
      })

    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [date.getTime()])

  function handleSelectRange(_columnIndex: number, startMinutes: number, endMinutes: number) {
    setPendingRange({
      start: dateAtMinutes(date, startMinutes),
      end: dateAtMinutes(date, endMinutes),
    })
  }

  const gridActivities: TimeGridActivity[] = activities.flatMap((activity) => {
    const start = new Date(activity.startDateTime)
    const end = new Date(activity.endDateTime)
    if (!isSameDate(date, start)) return []

    return [
      {
        id: activity.id,
        columnIndex: 0,
        startMinutes: start.getHours() * 60 + start.getMinutes(),
        endMinutes: isSameDate(start, end) ? end.getHours() * 60 + end.getMinutes() : 24 * 60,
        activityType: activity.activityType,
        location: activity.location,
      },
    ]
  })

  if (isLoading) {
    return (
      <div className="flex min-h-0 flex-1 items-center justify-center">
        <Loader2 size={24} className="animate-spin text-text-muted" />
      </div>
    )
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <p className="pb-3 text-sm text-text-subtle">Click an hour or drag across a range to log an activity.</p>
      {loadError && <p className="pb-3 text-sm text-red-400">{loadError}</p>}

      <div
        key={date.toISOString()}
        className="animate-calendar-slide flex min-h-0 flex-1 flex-col"
        style={{ '--slide-from': `${direction * 24}px` } as CSSProperties}
      >
        <TimeGrid
          columnCount={1}
          isColumnToday={() => isToday}
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
        <ActivityDetailDrawer
          activityId={selectedActivityId}
          onClose={() => setSelectedActivityId(null)}
          onActivityUpdated={(updated) =>
            setActivities((prev) => prev.map((activity) => (activity.id === updated.id ? updated : activity)))
          }
          onActivityDeleted={(deletedId) =>
            setActivities((prev) => prev.filter((activity) => activity.id !== deletedId))
          }
        />
      )}
    </div>
  )
}
