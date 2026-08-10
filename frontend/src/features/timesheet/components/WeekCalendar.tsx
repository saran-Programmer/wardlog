import { useState, type CSSProperties } from 'react'
import { useUser } from '../../../hooks/useUser'
import { dateAtMinutes } from '../../../lib/date'
import { TimeGrid } from './TimeGrid'
import { CreateActivityModal } from './CreateActivityModal'

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

  function handleSelectRange(columnIndex: number, startMinutes: number, endMinutes: number) {
    const day = days[columnIndex]
    setPendingRange({
      start: dateAtMinutes(day, startMinutes),
      end: dateAtMinutes(day, endMinutes),
    })
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <p className="pb-3 text-sm text-text-subtle">Click an hour or drag across a range to log an activity.</p>

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
        />
      </div>

      {pendingRange && user && (
        <CreateActivityModal
          doctorId={user.id}
          start={pendingRange.start}
          end={pendingRange.end}
          onClose={() => setPendingRange(null)}
          onCreated={() => setPendingRange(null)}
        />
      )}
    </div>
  )
}
