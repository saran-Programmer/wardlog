import { useEffect, useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { IconRail } from '../../components/IconRail'
import { useUser } from '../../hooks/useUser'
import { getMonthStatus } from '../../api/monthClose'
import { MonthCalendar } from './components/MonthCalendar'
import { WeekCalendar } from './components/WeekCalendar'
import { DayCalendar } from './components/DayCalendar'
import { MonthCloseTab } from './components/MonthCloseTab'
import { CloseMonthModal } from './components/CloseMonthModal'
import type { MonthStatusResponse } from '../../types/timesheet'

type ActivitiesTab = 'activities' | 'month-close'
type CalendarView = 'month' | 'week' | 'day'

const monthLabelFormat = new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' })
const weekPartFormat = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' })
const dayLabelFormat = new Intl.DateTimeFormat('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
const closedDateFormat = new Intl.DateTimeFormat('en-US', { month: 'long', day: 'numeric', year: 'numeric' })

function startOfWeek(date: Date) {
  const start = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  start.setDate(start.getDate() - start.getDay())
  return start
}

function startOfDay(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate())
}

export function TimesheetPage() {
  const { user } = useUser()
  const [activeTab, setActiveTab] = useState<ActivitiesTab>('activities')
  const [view, setView] = useState<CalendarView>('month')
  const [currentMonth, setCurrentMonth] = useState(() => {
    const now = new Date()
    return new Date(now.getFullYear(), now.getMonth(), 1)
  })
  const [weekStart, setWeekStart] = useState(() => startOfWeek(new Date()))
  const [dayDate, setDayDate] = useState(() => startOfDay(new Date()))
  const [direction, setDirection] = useState<1 | -1>(1)
  const [monthStatus, setMonthStatus] = useState<MonthStatusResponse | null>(null)
  const [isLoadingMonthStatus, setIsLoadingMonthStatus] = useState(false)
  const [showCloseModal, setShowCloseModal] = useState(false)

  useEffect(() => {
    if (activeTab !== 'month-close') return
    let cancelled = false
    setIsLoadingMonthStatus(true)

    getMonthStatus(currentMonth.getFullYear(), currentMonth.getMonth() + 1)
      .then((status) => {
        if (!cancelled) setMonthStatus(status)
      })
      .catch(() => {
        if (!cancelled) setMonthStatus(null)
      })
      .finally(() => {
        if (!cancelled) setIsLoadingMonthStatus(false)
      })

    return () => {
      cancelled = true
    }
  }, [activeTab, currentMonth])

  function goToPrevious() {
    setDirection(-1)
    if (activeTab === 'month-close' || view === 'month') {
      setCurrentMonth((prev) => new Date(prev.getFullYear(), prev.getMonth() - 1, 1))
    } else if (view === 'week') {
      setWeekStart((prev) => {
        const next = new Date(prev)
        next.setDate(next.getDate() - 7)
        return next
      })
    } else {
      setDayDate((prev) => {
        const next = new Date(prev)
        next.setDate(next.getDate() - 1)
        return next
      })
    }
  }

  function goToNext() {
    setDirection(1)
    if (activeTab === 'month-close' || view === 'month') {
      setCurrentMonth((prev) => new Date(prev.getFullYear(), prev.getMonth() + 1, 1))
    } else if (view === 'week') {
      setWeekStart((prev) => {
        const next = new Date(prev)
        next.setDate(next.getDate() + 7)
        return next
      })
    } else {
      setDayDate((prev) => {
        const next = new Date(prev)
        next.setDate(next.getDate() + 1)
        return next
      })
    }
  }

  function goToToday() {
    const now = new Date()
    if (activeTab === 'month-close' || view === 'month') {
      const target = new Date(now.getFullYear(), now.getMonth(), 1)
      setDirection(target.getTime() >= currentMonth.getTime() ? 1 : -1)
      setCurrentMonth(target)
    } else if (view === 'week') {
      const target = startOfWeek(now)
      setDirection(target.getTime() >= weekStart.getTime() ? 1 : -1)
      setWeekStart(target)
    } else {
      const target = startOfDay(now)
      setDirection(target.getTime() >= dayDate.getTime() ? 1 : -1)
      setDayDate(target)
    }
  }

  function handleSelectDay(date: Date) {
    const target = startOfWeek(date)
    setDirection(target.getTime() >= weekStart.getTime() ? 1 : -1)
    setWeekStart(target)
    setView('week')
  }

  const monthLabel = monthLabelFormat.format(currentMonth)
  const weekEnd = new Date(weekStart)
  weekEnd.setDate(weekStart.getDate() + 6)
  const weekLabel = `${weekPartFormat.format(weekStart)} – ${weekPartFormat.format(weekEnd)}, ${weekEnd.getFullYear()}`
  const dayLabel = dayLabelFormat.format(dayDate)
  const periodLabel =
    activeTab === 'month-close' || view === 'month' ? monthLabel : view === 'week' ? weekLabel : dayLabel
  const periodUnit = activeTab === 'month-close' ? 'month' : view

  return (
    <div className="flex h-screen bg-bg">
      <IconRail />

      <div className="flex min-h-0 flex-1 flex-col p-8">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text">Timesheet</h1>
            {user && (
              <p className="mt-1 text-sm text-text-muted">
                Dr. {user.name}
                {user.speciality ? ` · ${user.speciality}` : ''}
              </p>
            )}
          </div>

          <div className="flex items-center gap-6">
            {activeTab === 'activities' && (
              <button
                type="button"
                onClick={goToToday}
                className="rounded-lg bg-text px-3 py-1.5 text-sm font-semibold text-bg hover:opacity-90"
              >
                Today
              </button>
            )}

            <div className="flex items-center gap-3 rounded-lg bg-surface px-3 py-2">
              <button
                type="button"
                onClick={goToPrevious}
                aria-label={`Previous ${periodUnit}`}
                className="text-text-muted hover:text-text"
              >
                <ChevronLeft size={16} />
              </button>
              <span className="text-sm font-semibold text-text">{periodLabel}</span>
              <button
                type="button"
                onClick={goToNext}
                aria-label={`Next ${periodUnit}`}
                className="text-text-muted hover:text-text"
              >
                <ChevronRight size={16} />
              </button>
            </div>

            {activeTab === 'activities' && (
              <div className="flex items-center gap-1 rounded-lg bg-surface p-1">
                {(['month', 'week', 'day'] as const).map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => setView(option)}
                    className={`rounded-md px-3 py-1.5 text-sm font-medium capitalize ${
                      view === option ? 'bg-text text-bg' : 'text-text-muted hover:text-text'
                    }`}
                  >
                    {option}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="mt-6 flex items-center justify-between border-b border-white/10">
          <div className="flex gap-6">
            <button
              type="button"
              onClick={() => setActiveTab('activities')}
              className={`pb-3 text-sm font-semibold ${
                activeTab === 'activities' ? 'border-b-2 border-text text-text' : 'text-text-muted hover:text-text'
              }`}
            >
              Activities
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('month-close')}
              className={`pb-3 text-sm font-semibold ${
                activeTab === 'month-close' ? 'border-b-2 border-text text-text' : 'text-text-muted hover:text-text'
              }`}
            >
              Month Close
            </button>
          </div>

          {activeTab === 'month-close' && !isLoadingMonthStatus && (
            <div className="flex items-center gap-4 pb-3">
              {monthStatus?.closed ? (
                <p className="text-sm text-text-muted">
                  Closed{monthStatus.closedAt ? ` on ${closedDateFormat.format(new Date(monthStatus.closedAt))}` : ''}
                </p>
              ) : (
                <button
                  type="button"
                  onClick={() => setShowCloseModal(true)}
                  className="shrink-0 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-bg transition-opacity hover:opacity-90"
                >
                  Close Month
                </button>
              )}
            </div>
          )}
        </div>

        {activeTab === 'activities' ? (
          <div className="mt-4 flex min-h-0 flex-1 flex-col">
            {view === 'month' ? (
              <MonthCalendar monthDate={currentMonth} direction={direction} onSelectDay={handleSelectDay} />
            ) : view === 'week' ? (
              <WeekCalendar weekStart={weekStart} direction={direction} />
            ) : (
              <DayCalendar date={dayDate} direction={direction} />
            )}
          </div>
        ) : (
          <MonthCloseTab monthDate={currentMonth} />
        )}
      </div>

      {showCloseModal && (
        <CloseMonthModal
          year={currentMonth.getFullYear()}
          month={currentMonth.getMonth() + 1}
          onClose={() => setShowCloseModal(false)}
          onClosed={(closure) => {
            setMonthStatus({ closed: true, closedAt: closure.closedAt })
            setShowCloseModal(false)
          }}
        />
      )}
    </div>
  )
}
