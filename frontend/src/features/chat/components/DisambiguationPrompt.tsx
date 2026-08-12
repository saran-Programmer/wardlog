import { useState } from 'react'
import { MapPin, StickyNote } from 'lucide-react'
import { ApiError } from '../../../api/client'
import { resumeDisambiguation } from '../../../api/conversations'
import { describeProposedActivityType } from '../../../lib/proposedActivity'
import { DISAMBIGUATION_QUERY_CHOICE } from '../../../types/chat'
import type { DisambiguationOption, SendMessageDisambiguationInterrupt, SendMessageResponse } from '../../../types/chat'

const dateFormat = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' })
const timeFormat = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit' })

function summarizeOption(option: DisambiguationOption): string {
  const style = describeProposedActivityType(option.type)
  const start = option.start ? new Date(option.start) : null
  const end = option.end ? new Date(option.end) : null

  if (!start) return style.label
  const dateLabel = dateFormat.format(start)
  const timeLabel = end ? `${timeFormat.format(start)} – ${timeFormat.format(end)}` : timeFormat.format(start)
  return `${style.label}, ${dateLabel}, ${timeLabel}`
}

interface DisambiguationPromptProps {
  conversationId: string
  interrupt: SendMessageDisambiguationInterrupt
  onResolved: (humanSummary: string, response: SendMessageResponse) => void
}

export function DisambiguationPrompt({ conversationId, interrupt, onResolved }: DisambiguationPromptProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [queryText, setQueryText] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function submit(choice: string, humanSummary: string, text?: string) {
    setError(null)
    setIsSubmitting(true)
    try {
      const response = await resumeDisambiguation(conversationId, choice, text)
      onResolved(humanSummary, response)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not submit your choice. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  function handleSelectConfirm() {
    if (!selectedId) return
    const option = interrupt.options.find((o) => o.id === selectedId)
    if (!option) return
    submit(selectedId, summarizeOption(option))
  }

  function handleQuerySubmit() {
    const trimmed = queryText.trim()
    if (!trimmed) return
    submit(DISAMBIGUATION_QUERY_CHOICE, trimmed, trimmed)
  }

  return (
    <div className="w-full max-w-xl space-y-3 rounded-2xl border border-white/5 bg-surface p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-text-subtle">
        Which activity did you mean?
      </p>

      <div className="space-y-2">
        {interrupt.options.map((option) => {
          const style = describeProposedActivityType(option.type)
          const start = option.start ? new Date(option.start) : null
          const end = option.end ? new Date(option.end) : null
          const isSelected = selectedId === option.id

          return (
            <button
              key={option.id}
              type="button"
              disabled={isSubmitting}
              onClick={() => setSelectedId(option.id)}
              className={`w-full rounded-xl border p-3 text-left transition-colors disabled:opacity-60 ${
                isSelected ? 'border-accent/60 bg-surface-raised' : 'border-white/5 bg-surface-raised hover:border-white/15'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${style.chipBg} text-bg`}>
                  {style.label}
                </span>
                <span
                  aria-hidden
                  className={`mt-0.5 h-4 w-4 shrink-0 rounded-full border ${
                    isSelected ? 'border-accent bg-accent' : 'border-white/20'
                  }`}
                />
              </div>

              <div className="mt-2 space-y-1">
                <p className="text-sm font-medium text-text">
                  {start ? dateFormat.format(start) : 'No date set'}
                </p>
                <p className="text-sm text-text-muted">
                  {start && end
                    ? `${timeFormat.format(start)} – ${timeFormat.format(end)}`
                    : start
                      ? `Starts ${timeFormat.format(start)}`
                      : 'No time set'}
                </p>
                <div className="flex items-center gap-1.5 text-sm text-text-subtle">
                  <MapPin size={13} className="shrink-0" />
                  <span>{option.location || 'No location'}</span>
                </div>
                {option.notes && (
                  <div className="flex items-start gap-1.5 pt-1 text-sm text-text-subtle">
                    <StickyNote size={13} className="mt-0.5 shrink-0" />
                    <span className="whitespace-pre-wrap">{option.notes}</span>
                  </div>
                )}
              </div>
            </button>
          )
        })}
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      <button
        type="button"
        onClick={handleSelectConfirm}
        disabled={isSubmitting || !selectedId}
        className="w-full rounded-lg bg-accent py-2.5 text-sm font-semibold text-bg transition-opacity hover:opacity-90 disabled:opacity-60"
      >
        {isSubmitting ? 'Submitting…' : 'Use this activity'}
      </button>

      {interrupt.allow_query && (
        <div className="space-y-2 border-t border-white/5 pt-3">
          <p className="text-xs text-text-subtle">Or describe which one you mean</p>
          <div className="flex gap-2">
            <input
              type="text"
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              placeholder="e.g. the one at Ward 5 in the afternoon"
              disabled={isSubmitting}
              className="flex-1 rounded-lg border border-white/5 bg-input px-3 py-2 text-sm text-text placeholder:text-text-subtle focus:border-accent focus:outline-none disabled:opacity-60"
            />
            <button
              type="button"
              onClick={handleQuerySubmit}
              disabled={isSubmitting || !queryText.trim()}
              className="shrink-0 rounded-lg border border-white/10 px-3 py-2 text-sm font-medium text-text transition-colors hover:border-white/20 disabled:opacity-60"
            >
              Ask
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
