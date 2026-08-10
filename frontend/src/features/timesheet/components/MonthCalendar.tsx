import { useEffect, useLayoutEffect, useRef, useState, type CSSProperties } from 'react'
import { MoreHorizontal } from 'lucide-react'
import { getActivities } from '../../../api/activities'
import { ApiError } from '../../../api/client'
import { getActivityTypeOption } from '../../../lib/activityType'
import { toDateInputValue } from '../../../lib/date'
import type { ActivityResponse } from '../../../types/timesheet'

const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const GAP = 12
const MAX_ROWS = 6
const MAX_VISIBLE_CHIPS = 2
const chipTimeFormat = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit' })

interface MonthCalendarProps {
  monthDate: Date
  direction: 1 | -1
  onSelectDay: (date: Date) => void
}

export function MonthCalendar({ monthDate, direction, onSelectDay }: MonthCalendarProps) {
  const year = monthDate.getFullYear()
  const month = monthDate.getMonth()
  const today = new Date()

  const firstWeekday = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const rows = Math.ceil((firstWeekday + daysInMonth) / 7)

  const cells = Array.from({ length: rows * 7 }, (_, index) => {
    const day = index - firstWeekday + 1
    return day >= 1 && day <= daysInMonth ? day : null
  })

  function isToday(day: number) {
    return day === today.getDate() && month === today.getMonth() && year === today.getFullYear()
  }

  const [activities, setActivities] = useState<ActivityResponse[]>([])
  const [loadError, setLoadError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoadError(null)
    const startDate = toDateInputValue(new Date(year, month, 1))
    const endDate = toDateInputValue(new Date(year, month, daysInMonth))

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
  }, [year, month, daysInMonth])

  const activitiesByDay = new Map<number, ActivityResponse[]>()
  activities.forEach((activity) => {
    const start = new Date(activity.startDateTime)
    if (start.getMonth() !== month || start.getFullYear() !== year) return
    const day = start.getDate()
    const dayActivities = activitiesByDay.get(day) ?? []
    dayActivities.push(activity)
    activitiesByDay.set(day, dayActivities)
  })
  activitiesByDay.forEach((dayActivities) =>
    dayActivities.sort((a, b) => a.startDateTime.localeCompare(b.startDateTime)),
  )

  const containerRef = useRef<HTMLDivElement>(null)
  const [rowHeight, setRowHeight] = useState(0)

  useLayoutEffect(() => {
    const container = containerRef.current
    if (!container) return

    function measure() {
      const { width, height } = container!.getBoundingClientRect()
      const columnWidth = (width - GAP * 6) / 7
      const byHeight = (height - GAP * (MAX_ROWS - 1)) / MAX_ROWS
      setRowHeight(Math.max(0, Math.floor(Math.min(columnWidth, byHeight))))
    }

    measure()
    const observer = new ResizeObserver(measure)
    observer.observe(container)
    return () => observer.disconnect()
  }, [])

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      {loadError && <p className="pb-2 text-sm text-red-400">{loadError}</p>}

      <div className="grid grid-cols-7">
        {WEEKDAYS.map((day) => (
          <div key={day} className="pb-2 text-center text-sm font-medium text-text-muted">
            {day}
          </div>
        ))}
      </div>

      <div ref={containerRef} className="min-h-0 flex-1">
        {rowHeight > 0 && (
          <div
            key={`${year}-${month}`}
            className="animate-calendar-slide grid grid-cols-7"
            style={
              {
                gridTemplateRows: `repeat(${rows}, ${rowHeight}px)`,
                gap: `${GAP}px`,
                '--slide-from': `${direction * 24}px`,
              } as CSSProperties
            }
          >
            {cells.map((day, index) => {
              const dayActivities = day !== null ? activitiesByDay.get(day) : undefined
              const visibleActivities = dayActivities?.slice(0, MAX_VISIBLE_CHIPS)
              const hiddenCount = dayActivities ? dayActivities.length - MAX_VISIBLE_CHIPS : 0

              return (
                <div
                  key={index}
                  onClick={day !== null ? () => onSelectDay(new Date(year, month, day)) : undefined}
                  className={`overflow-hidden rounded-xl border p-2 transition-colors ${
                    day !== null
                      ? 'cursor-pointer border-white/10 bg-bg hover:bg-surface-raised'
                      : 'border-white/5 bg-bg/60 opacity-40'
                  }`}
                >
                  {day !== null && (
                    <>
                      <span
                        className={`inline-flex h-6 w-6 items-center justify-center rounded-full text-sm font-medium ${
                          isToday(day) ? 'bg-accent text-bg' : 'text-text'
                        }`}
                      >
                        {day}
                      </span>
                      {visibleActivities && visibleActivities.length > 0 && (
                        <div className="mt-1.5 space-y-1">
                          {visibleActivities.map((activity) => {
                            const option = getActivityTypeOption(activity.activityType)
                            return (
                              <p
                                key={activity.id}
                                className={`truncate rounded-md px-1.5 py-0.5 text-xs font-medium ${option.bg} ${option.text}`}
                              >
                                {chipTimeFormat.format(new Date(activity.startDateTime))} {option.label}
                              </p>
                            )
                          })}
                          {hiddenCount > 0 && (
                            <div className="flex items-center gap-1 px-1.5 text-text-subtle">
                              <MoreHorizontal size={12} />
                              <span className="text-xs">{hiddenCount} more</span>
                            </div>
                          )}
                        </div>
                      )}
                    </>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
