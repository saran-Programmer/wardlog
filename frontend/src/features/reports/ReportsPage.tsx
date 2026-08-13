import { BarChart2, ChevronRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { IconRail } from '../../components/IconRail'

const reports = [
  {
    to: '/reports/activity-comparison',
    icon: BarChart2,
    title: 'Activity Comparison',
    description: 'Bar chart comparing how much work is done across activity types over a date range',
  },
]

export function ReportsPage() {
  return (
    <div className="flex h-screen bg-bg">
      <IconRail />

      <div className="flex min-h-0 flex-1 flex-col p-8">
        <h1 className="text-2xl font-bold text-text">Reports</h1>
        <p className="mt-1 text-sm text-text-muted">Choose a report to explore.</p>

        <div className="mt-6 flex flex-col gap-4">
          {reports.map(({ to, icon: Icon, title, description }) => (
            <Link
              key={to}
              to={to}
              className="flex items-center gap-4 rounded-xl border border-white/10 bg-surface p-5 transition-colors hover:border-white/20"
            >
              <div className="flex h-10 w-10 flex-none items-center justify-center rounded-lg bg-accent-muted text-accent-strong">
                <Icon size={20} />
              </div>
              <div className="flex-1">
                <p className="font-semibold text-text">{title}</p>
                <p className="mt-1 text-sm text-text-muted">{description}</p>
              </div>
              <ChevronRight size={18} className="flex-none text-text-subtle" />
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
