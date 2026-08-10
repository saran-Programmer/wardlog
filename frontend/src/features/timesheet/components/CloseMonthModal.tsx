import { useState } from 'react'
import { X } from 'lucide-react'
import { closeMonth } from '../../../api/monthClose'
import { ApiError } from '../../../api/client'
import type { MonthClosureResponse } from '../../../types/timesheet'

const monthLabelFormat = new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' })

interface CloseMonthModalProps {
  year: number
  month: number
  onClose: () => void
  onClosed: (closure: MonthClosureResponse) => void
}

export function CloseMonthModal({ year, month, onClose, onClosed }: CloseMonthModalProps) {
  const [error, setError] = useState<string | null>(null)
  const [isClosing, setIsClosing] = useState(false)

  const monthLabel = monthLabelFormat.format(new Date(year, month - 1, 1))

  async function handleConfirm() {
    setError(null)
    setIsClosing(true)

    try {
      const closure = await closeMonth({ year, month })
      onClosed(closure)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Unable to close this month. Please try again.')
      setIsClosing(false)
    }
  }

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-md rounded-2xl border border-white/5 bg-surface p-6">
        <div className="mb-1 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-text">Close {monthLabel}?</h2>
          <button type="button" onClick={onClose} aria-label="Close" className="text-text-muted hover:text-text">
            <X size={18} />
          </button>
        </div>

        <p className="mb-5 text-sm text-text-muted">
          This is permanent. Once {monthLabel} is closed, its logged activities can no longer be added, edited, or
          removed.
        </p>

        {error && <p className="mb-4 text-sm text-red-400">{error}</p>}

        <div className="flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            disabled={isClosing}
            className="rounded-lg border border-white/10 px-4 py-2 text-sm font-medium text-text hover:bg-white/5 disabled:opacity-60"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            disabled={isClosing}
            className="rounded-lg bg-accent px-5 py-2 text-sm font-semibold text-bg transition-opacity hover:opacity-90 disabled:opacity-60"
          >
            {isClosing ? 'Closing…' : 'Close Month'}
          </button>
        </div>
      </div>
    </div>
  )
}
