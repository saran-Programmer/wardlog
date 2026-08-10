import { useEffect, useLayoutEffect, useRef, useState } from 'react'

const HOURS = Array.from({ length: 24 }, (_, hour) => hour)
const ROW_HEIGHT = 64
const INITIAL_SCROLL_HOUR = 5.5
const SNAP_MINUTES = 30
const MAX_MINUTES = HOURS.length * 60

function formatHourLabel(hour: number) {
  if (hour === 0) return '12 AM'
  if (hour === 12) return '12 PM'
  return hour < 12 ? `${hour} AM` : `${hour - 12} PM`
}

function formatMinutesLabel(minutes: number) {
  const hourOfDay = Math.floor(minutes / 60) % 24
  const mins = minutes % 60
  const period = hourOfDay < 12 ? 'AM' : 'PM'
  const hour12 = hourOfDay % 12 === 0 ? 12 : hourOfDay % 12
  return `${hour12}:${mins.toString().padStart(2, '0')} ${period}`
}

function snapMinutes(rawMinutes: number) {
  const snapped = Math.round(rawMinutes / SNAP_MINUTES) * SNAP_MINUTES
  return Math.min(Math.max(snapped, 0), MAX_MINUTES)
}

interface DragState {
  column: number
  anchorMinutes: number
  currentMinutes: number
}

interface TimeGridProps {
  columnCount: number
  isColumnToday?: (columnIndex: number) => boolean
  onSelectRange?: (columnIndex: number, startMinutes: number, endMinutes: number) => void
}

export function TimeGrid({ columnCount, isColumnToday, onSelectRange }: TimeGridProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const hasScrolledRef = useRef(false)
  const columnRefs = useRef<(HTMLDivElement | null)[]>([])
  const dragRef = useRef<DragState | null>(null)
  const [drag, setDrag] = useState<DragState | null>(null)

  useLayoutEffect(() => {
    if (hasScrolledRef.current) return
    const el = scrollRef.current
    if (!el) return
    el.scrollTop = INITIAL_SCROLL_HOUR * ROW_HEIGHT
    hasScrolledRef.current = true
  }, [])

  function minutesFromPointer(columnIndex: number, clientY: number) {
    const el = columnRefs.current[columnIndex]
    if (!el) return null
    const rect = el.getBoundingClientRect()
    return snapMinutes(((clientY - rect.top) / ROW_HEIGHT) * 60)
  }

  function updateDrag(next: DragState) {
    dragRef.current = next
    setDrag(next)
  }

  function handleMouseDown(columnIndex: number, e: React.MouseEvent) {
    if (!onSelectRange) return
    const minutes = minutesFromPointer(columnIndex, e.clientY)
    if (minutes === null) return
    updateDrag({ column: columnIndex, anchorMinutes: minutes, currentMinutes: minutes })
  }

  useEffect(() => {
    if (!drag) return

    function handleMouseMove(e: MouseEvent) {
      const current = dragRef.current
      if (!current) return
      const minutes = minutesFromPointer(current.column, e.clientY)
      if (minutes === null) return
      updateDrag({ ...current, currentMinutes: minutes })
    }

    function handleMouseUp() {
      const current = dragRef.current
      dragRef.current = null
      setDrag(null)

      if (!current || !onSelectRange) return
      const startMinutes = Math.min(current.anchorMinutes, current.currentMinutes)
      let endMinutes = Math.max(current.anchorMinutes, current.currentMinutes)
      if (endMinutes <= startMinutes) {
        endMinutes = Math.min(startMinutes + 60, MAX_MINUTES)
      }
      if (endMinutes > startMinutes) {
        onSelectRange(current.column, startMinutes, endMinutes)
      }
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseup', handleMouseUp)
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [Boolean(drag), onSelectRange])

  return (
    <div ref={scrollRef} className="calendar-scroll min-h-0 flex-1 overflow-y-auto">
      <div className="flex" style={{ height: HOURS.length * ROW_HEIGHT }}>
        <div className="w-14 flex-shrink-0">
          {HOURS.map((hour) => (
            <div key={hour} className="relative border-t border-white/5" style={{ height: ROW_HEIGHT }}>
              {hour !== 0 && (
                <span className="pointer-events-none absolute right-2 top-0 -translate-y-1/2 text-xs font-medium text-text-muted">
                  {formatHourLabel(hour)}
                </span>
              )}
            </div>
          ))}
        </div>

        <div
          className="grid flex-1"
          style={{ gridTemplateColumns: `repeat(${columnCount}, minmax(0, 1fr))` }}
        >
          {Array.from({ length: columnCount }, (_, columnIndex) => (
            <div
              key={columnIndex}
              ref={(el) => {
                columnRefs.current[columnIndex] = el
              }}
              onMouseDown={(e) => handleMouseDown(columnIndex, e)}
              className={`relative border-l border-white/10 ${isColumnToday?.(columnIndex) ? 'bg-accent/5' : ''} ${
                drag ? 'select-none' : ''
              }`}
            >
              {HOURS.map((hour) => (
                <div
                  key={hour}
                  className="cursor-pointer border-t border-white/5 hover:bg-surface-raised/40"
                  style={{ height: ROW_HEIGHT }}
                />
              ))}

              {drag && drag.column === columnIndex && (
                <div
                  className="pointer-events-none absolute inset-x-0 rounded-xl border-2 border-accent-strong bg-accent/15 px-3 py-1.5"
                  style={{
                    top: (Math.min(drag.anchorMinutes, drag.currentMinutes) / 60) * ROW_HEIGHT,
                    height: Math.max(
                      ((Math.max(drag.anchorMinutes, drag.currentMinutes) - Math.min(drag.anchorMinutes, drag.currentMinutes)) /
                        60) *
                        ROW_HEIGHT,
                      4,
                    ),
                  }}
                >
                  <span className="text-xs font-semibold text-accent-strong">
                    {formatMinutesLabel(Math.min(drag.anchorMinutes, drag.currentMinutes))} –{' '}
                    {formatMinutesLabel(Math.max(drag.anchorMinutes, drag.currentMinutes))}
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
