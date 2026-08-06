import type { ReactNode } from 'react'
import logo from '../../../assets/logo-icon.png'

interface AuthLayoutProps {
  title: string
  subtitle: string
  children: ReactNode
}

const bullets = [
  'Dictate your day in plain language — no typing required.',
  "AI drafts your entries — you review and approve before anything's logged.",
  'Track hours, encounters, and documents in one place.',
]

export function AuthLayout({ title, subtitle, children }: AuthLayoutProps) {
  return (
    <div className="flex min-h-screen bg-bg">
      <div className="hidden w-1/2 flex-col items-center justify-between bg-gradient-to-br from-accent-muted to-bg p-12 lg:flex">
        <div className="flex flex-col items-center text-center">
          <div className="flex items-center gap-3">
            <img src={logo} alt="" className="h-auto w-12" />
            <span className="text-2xl font-bold uppercase tracking-wide text-text">WardLog</span>
          </div>

          <h1 className="mt-16 text-4xl font-bold leading-tight text-text">
            Spend less time charting, more time with patients.
          </h1>
          <p className="mt-4 text-lg text-text-muted">
            WardLog turns what you say at the end of a shift into a finished timesheet.
          </p>

          <ul className="mx-auto mt-10 max-w-sm space-y-4 text-left">
            {bullets.map((bullet) => (
              <li key={bullet} className="flex items-start gap-3">
                <span className="mt-0.5 flex h-5 w-5 flex-none items-center justify-center rounded-full bg-accent text-xs text-bg">
                  ✓
                </span>
                <span className="text-text-muted">{bullet}</span>
              </li>
            ))}
          </ul>
        </div>

        <p className="text-sm text-text-subtle">© 2026 WardLog</p>
      </div>

      <div className="flex w-full items-center justify-center px-6 py-12 lg:w-1/2">
        <div className="w-full max-w-sm">
          <h2 className="text-2xl font-bold text-text">{title}</h2>
          <p className="mt-1 text-text-muted">{subtitle}</p>

          <div className="mt-8">{children}</div>
        </div>
      </div>
    </div>
  )
}
