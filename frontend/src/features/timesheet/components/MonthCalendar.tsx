import { useLayoutEffect, useRef, useState, type CSSProperties } from 'react'

const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const GAP = 12

interface MonthCalendarProps {
  monthDate: Date
  direction: 1 | -1
}

export function MonthCalendar({ monthDate, direction }: MonthCalendarProps) {
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

  const containerRef = useRef<HTMLDivElement>(null)
  const [rowHeight, setRowHeight] = useState(0)

  useLayoutEffect(() => {
    const container = containerRef.current
    if (!container) return

    function measure() {
      const { width, height } = container!.getBoundingClientRect()
      const columnWidth = (width - GAP * 6) / 7
      const byHeight = (height - GAP * (rows - 1)) / rows
      setRowHeight(Math.max(0, Math.floor(Math.min(columnWidth, byHeight))))
    }

    measure()
    const observer = new ResizeObserver(measure)
    observer.observe(container)
    return () => observer.disconnect()
  }, [rows])

  return (
    <div className="flex min-h-0 flex-1 flex-col">
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
            className="animate-month-slide grid grid-cols-7"
            style={
              {
                gridTemplateRows: `repeat(${rows}, ${rowHeight}px)`,
                gap: `${GAP}px`,
                '--slide-from': `${direction * 24}px`,
              } as CSSProperties
            }
          >
            {cells.map((day, index) => (
              <div
                key={index}
                className={`rounded-xl border p-2 transition-colors ${
                  day !== null
                    ? 'cursor-pointer border-white/10 bg-bg hover:bg-surface-raised'
                    : 'border-white/5 bg-bg/60 opacity-40'
                }`}
              >
                {day !== null && (
                  <span
                    className={`inline-flex h-6 w-6 items-center justify-center rounded-full text-sm font-medium ${
                      isToday(day) ? 'bg-accent text-bg' : 'text-text'
                    }`}
                  >
                    {day}
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
