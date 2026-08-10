import { useState, type CSSProperties } from 'react'
import { useUser } from '../../../hooks/useUser'
import { dateAtMinutes } from '../../../lib/date'
import { TimeGrid } from './TimeGrid'
import { CreateActivityModal } from './CreateActivityModal'

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

  function handleSelectRange(_columnIndex: number, startMinutes: number, endMinutes: number) {
    setPendingRange({
      start: dateAtMinutes(date, startMinutes),
      end: dateAtMinutes(date, endMinutes),
    })
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <p className="pb-3 text-sm text-text-subtle">Click an hour or drag across a range to log an activity.</p>

      <div
        key={date.toISOString()}
        className="animate-calendar-slide flex min-h-0 flex-1 flex-col"
        style={{ '--slide-from': `${direction * 24}px` } as CSSProperties}
      >
        <TimeGrid columnCount={1} isColumnToday={() => isToday} onSelectRange={handleSelectRange} />
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
