import { useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { IconRail } from '../../components/IconRail'
import { useUser } from '../../hooks/useUser'
import { MonthCalendar } from './components/MonthCalendar'

type ActivitiesTab = 'activities' | 'month-close'
type CalendarView = 'month' | 'week' | 'day'

const monthLabelFormat = new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' })

export function TimesheetPage() {
  const { user } = useUser()
  const [activeTab, setActiveTab] = useState<ActivitiesTab>('activities')
  const [view, setView] = useState<CalendarView>('month')
  const [currentMonth, setCurrentMonth] = useState(() => {
    const now = new Date()
    return new Date(now.getFullYear(), now.getMonth(), 1)
  })
  const [direction, setDirection] = useState<1 | -1>(1)

  function goToPreviousMonth() {
    setDirection(-1)
    setCurrentMonth((prev) => new Date(prev.getFullYear(), prev.getMonth() - 1, 1))
  }

  function goToNextMonth() {
    setDirection(1)
    setCurrentMonth((prev) => new Date(prev.getFullYear(), prev.getMonth() + 1, 1))
  }

  function goToToday() {
    const now = new Date()
    const target = new Date(now.getFullYear(), now.getMonth(), 1)
    setDirection(target.getTime() >= currentMonth.getTime() ? 1 : -1)
    setCurrentMonth(target)
  }

  const monthLabel = monthLabelFormat.format(currentMonth)

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
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-accent-strong">45h</span>
                <span className="text-sm text-text-muted">logged this period</span>
              </div>
            )}

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
                onClick={goToPreviousMonth}
                aria-label="Previous month"
                className="text-text-muted hover:text-text"
              >
                <ChevronLeft size={16} />
              </button>
              <span className="text-sm font-semibold text-text">{monthLabel}</span>
              <button
                type="button"
                onClick={goToNextMonth}
                aria-label="Next month"
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

        <div className="mt-6 flex items-center border-b border-white/10">
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
        </div>

        {activeTab === 'activities' ? (
          <div className="mt-4 flex min-h-0 flex-1 flex-col">
            {view === 'month' ? (
              <MonthCalendar monthDate={currentMonth} direction={direction} />
            ) : (
              <div className="flex flex-1 items-center justify-center text-text-muted">
                {view === 'week' ? 'Week view coming soon' : 'Day view coming soon'}
              </div>
            )}
          </div>
        ) : (
          <div className="mt-6 flex flex-1 items-center justify-center text-text-muted">Month Close coming soon</div>
        )}
      </div>
    </div>
  )
}
