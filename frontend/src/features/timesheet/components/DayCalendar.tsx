import { useState, type CSSProperties } from 'react'
import { useUser } from '../../../hooks/useUser'
import { dateAtMinutes } from '../../../lib/date'
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

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <p className="pb-3 text-sm text-text-subtle">Click an hour or drag across a range to log an activity.</p>

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
        <ActivityDetailDrawer activityId={selectedActivityId} onClose={() => setSelectedActivityId(null)} />
      )}
    </div>
  )
}
