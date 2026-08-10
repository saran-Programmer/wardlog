import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChevronLeft } from 'lucide-react'
import { Bar, BarChart, CartesianGrid, Cell, LabelList, ResponsiveContainer, XAxis, YAxis } from 'recharts'
import { IconRail } from '../../components/IconRail'
import { AskReportPanel } from './components/AskReportPanel'
import { getActivityComparison } from '../../api/reports'
import { getActivityTypeOption } from '../../lib/activityType'
import { toDateInputValue } from '../../lib/date'
import type { ActivityComparisonResponse } from '../../types/timesheet'

type Preset = 'week' | 'month' | 'last-month' | 'custom'
type Metric = 'count' | 'hours'

const rangeLabelFormat = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' })

const presets: { value: Preset; label: string }[] = [
  { value: 'week', label: 'This Week' },
  { value: 'month', label: 'This Month' },
  { value: 'last-month', label: 'Last Month' },
  { value: 'custom', label: 'Custom' },
]

const metrics: { value: Metric; label: string }[] = [
  { value: 'count', label: 'Number of Activities' },
  { value: 'hours', label: 'Hours Worked' },
]

function startOfWeek(date: Date) {
  const start = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  start.setDate(start.getDate() - start.getDay())
  return start
}

function presetRange(preset: Preset): { from: Date; to: Date } {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())

  if (preset === 'week') return { from: startOfWeek(today), to: today }
  if (preset === 'month') return { from: new Date(today.getFullYear(), today.getMonth(), 1), to: today }
  if (preset === 'last-month') {
    return {
      from: new Date(today.getFullYear(), today.getMonth() - 1, 1),
      to: new Date(today.getFullYear(), today.getMonth(), 0),
    }
  }
  return { from: today, to: today }
}

export function ActivityComparisonPage() {
  const navigate = useNavigate()
  const [preset, setPreset] = useState<Preset>('month')
  const [range, setRange] = useState(() => presetRange('month'))
  const [metric, setMetric] = useState<Metric>('count')
  const [data, setData] = useState<ActivityComparisonResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setIsLoading(true)
    setError(null)

    getActivityComparison(range.from, range.to)
      .then((response) => {
        if (!cancelled) setData(response)
      })
      .catch(() => {
        if (!cancelled) setError('Could not load this report. Please try again.')
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [range])

  function handlePresetChange(next: Preset) {
    setPreset(next)
    if (next !== 'custom') setRange(presetRange(next))
  }

  const chartData = useMemo(() => {
    if (!data) return []
    return data.breakdown.map((entry) => {
      const option = getActivityTypeOption(entry.activityType)
      return {
        name: option.label,
        value: metric === 'count' ? entry.activityCount : Math.round((entry.totalMinutes / 60) * 10) / 10,
        color: option.hex,
      }
    })
  }, [data, metric])

  const hasActivity = chartData.some((entry) => entry.value > 0)
  const rangeLabel = `${rangeLabelFormat.format(range.from)} – ${rangeLabelFormat.format(range.to)}`

  return (
    <div className="flex h-screen bg-bg">
      <IconRail />

      <div className="flex min-h-0 flex-1 flex-col overflow-y-auto p-8">
        <div className="flex items-start gap-3">
          <button
            type="button"
            onClick={() => navigate('/reports')}
            aria-label="Back to reports"
            className="mt-1 text-text-muted hover:text-text"
          >
            <ChevronLeft size={20} />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-text">Activity Comparison</h1>
            <p className="mt-1 text-sm text-text-muted">
              See how your logged work breaks down across activity types
            </p>
          </div>
        </div>

        <div className="mt-6 flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-1 rounded-lg bg-surface p-1">
            {presets.map(({ value, label }) => (
              <button
                key={value}
                type="button"
                onClick={() => handlePresetChange(value)}
                className={`rounded-md px-3 py-1.5 text-sm font-medium ${
                  preset === value ? 'bg-text text-bg' : 'text-text-muted hover:text-text'
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2 rounded-lg bg-surface px-3 py-2">
            <input
              type="date"
              value={toDateInputValue(range.from)}
              disabled={preset !== 'custom'}
              onChange={(event) => {
                const value = event.target.value
                if (value) setRange((prev) => ({ ...prev, from: new Date(value) }))
              }}
              className="bg-transparent text-sm text-text disabled:opacity-70"
            />
            <span className="text-sm text-text-muted">to</span>
            <input
              type="date"
              value={toDateInputValue(range.to)}
              disabled={preset !== 'custom'}
              onChange={(event) => {
                const value = event.target.value
                if (value) setRange((prev) => ({ ...prev, to: new Date(value) }))
              }}
              className="bg-transparent text-sm text-text disabled:opacity-70"
            />
          </div>

          <div className="flex items-center gap-1 rounded-lg bg-surface p-1">
            {metrics.map(({ value, label }) => (
              <button
                key={value}
                type="button"
                onClick={() => setMetric(value)}
                className={`rounded-md px-3 py-1.5 text-sm font-medium ${
                  metric === value ? 'bg-text text-bg' : 'text-text-muted hover:text-text'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <p className="mt-4 text-sm text-text-muted">{rangeLabel}</p>

        <div className="mt-4 flex min-h-0 flex-1 gap-6">
          <div className="flex-1 rounded-xl border border-white/10 bg-surface p-6">
            <p className="text-xs font-semibold tracking-wide text-text-subtle">
              {metric === 'count' ? 'NUMBER OF ACTIVITIES' : 'HOURS WORKED'}
            </p>

            <div className="mt-4 h-[420px]">
              {isLoading ? (
                <div className="flex h-full items-center justify-center text-sm text-text-muted">Loading…</div>
              ) : error ? (
                <div className="flex h-full items-center justify-center text-sm text-red-400">{error}</div>
              ) : !hasActivity ? (
                <div className="flex h-full items-center justify-center text-sm text-text-muted">
                  No activities logged in this range.
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 24, right: 8, left: 0, bottom: 0 }}>
                    <CartesianGrid vertical={false} stroke="rgba(255,255,255,0.08)" />
                    <XAxis
                      dataKey="name"
                      tick={{ fill: '#9aa4a8', fontSize: 13, fontWeight: 600 }}
                      axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
                      tickLine={false}
                    />
                    <YAxis
                      allowDecimals={metric === 'hours'}
                      tick={{ fill: '#9aa4a8', fontSize: 12 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <Bar dataKey="value" radius={[6, 6, 0, 0]} maxBarSize={72}>
                      <LabelList
                        dataKey="value"
                        position="top"
                        formatter={(value) => (metric === 'hours' ? `${value}h` : `${value}`)}
                        fill="#f5f7f7"
                        fontWeight={700}
                      />
                      {chartData.map((entry) => (
                        <Cell key={entry.name} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          <AskReportPanel />
        </div>
      </div>
    </div>
  )
}
