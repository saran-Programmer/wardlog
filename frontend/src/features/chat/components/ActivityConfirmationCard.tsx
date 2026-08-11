import { Check, MapPin, Pencil, StickyNote, X } from 'lucide-react'
import { formatDuration } from '../../../lib/date'
import { PROPOSED_ACTIVITY_TYPE_OPTIONS, describeProposedActivityType } from '../../../lib/proposedActivity'
import type { ActivityDecisionKind, ProposedActivity } from '../../../types/chat'

const dateFormat = new Intl.DateTimeFormat('en-US', {
  weekday: 'long',
  month: 'long',
  day: 'numeric',
  year: 'numeric',
})
const timeFormat = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit' })

export interface CardFields {
  type: string
  start: string
  end: string
  location: string
  notes: string
}

export interface CardState {
  decision: ActivityDecisionKind
  fields: CardFields
}

export function initialCardState(activity: ProposedActivity): CardState {
  return {
    decision: 'accept',
    fields: {
      type: activity.type,
      start: activity.start ? activity.start.slice(0, 16) : '',
      end: activity.end ? activity.end.slice(0, 16) : '',
      location: activity.location ?? '',
      notes: activity.notes ?? '',
    },
  }
}

interface ActivityConfirmationCardProps {
  activity: ProposedActivity
  state: CardState
  onChange: (next: CardState) => void
  locked: boolean
}

export function ActivityConfirmationCard({ activity, state, onChange, locked }: ActivityConfirmationCardProps) {
  const { decision, fields } = state
  const isEditing = decision === 'edit' && !locked

  const displaySource =
    locked && decision === 'edit'
      ? {
          type: fields.type,
          start: fields.start ? `${fields.start}:00` : null,
          end: fields.end ? `${fields.end}:00` : null,
          location: fields.location || null,
          notes: fields.notes || null,
        }
      : { type: activity.type, start: activity.start, end: activity.end, location: activity.location, notes: activity.notes }

  const style = describeProposedActivityType(displaySource.type)

  const typeOptions = PROPOSED_ACTIVITY_TYPE_OPTIONS.some((option) => option.value === activity.type.toLowerCase())
    ? PROPOSED_ACTIVITY_TYPE_OPTIONS
    : [{ value: activity.type, label: style.label }, ...PROPOSED_ACTIVITY_TYPE_OPTIONS]

  const startDate = displaySource.start ? new Date(displaySource.start) : null
  const endDate = displaySource.end ? new Date(displaySource.end) : null
  const durationMinutes =
    startDate && endDate ? Math.round((endDate.getTime() - startDate.getTime()) / 60000) : null

  function setDecision(next: ActivityDecisionKind) {
    onChange({ ...state, decision: next })
  }

  function setField<K extends keyof CardFields>(key: K, value: CardFields[K]) {
    onChange({ ...state, fields: { ...fields, [key]: value } })
  }

  return (
    <div
      className={`rounded-2xl border p-4 transition-colors ${
        decision === 'reject'
          ? 'border-white/5 bg-surface-raised opacity-50'
          : decision === 'accept'
            ? 'border-accent/30 bg-surface-raised'
            : 'border-white/10 bg-surface-raised'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <span className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ${style.chipBg} text-bg`}>
          {style.label}
        </span>

        {!locked ? (
          <div className="flex items-center gap-1 rounded-full border border-white/10 p-1">
            <button
              type="button"
              aria-pressed={decision === 'accept'}
              aria-label="Accept"
              onClick={() => setDecision('accept')}
              className={`flex h-7 w-7 items-center justify-center rounded-full transition-colors ${
                decision === 'accept' ? 'bg-accent text-bg' : 'text-text-muted hover:text-text'
              }`}
            >
              <Check size={14} />
            </button>
            <button
              type="button"
              aria-pressed={decision === 'edit'}
              aria-label="Edit"
              onClick={() => setDecision('edit')}
              className={`flex h-7 w-7 items-center justify-center rounded-full transition-colors ${
                decision === 'edit' ? 'bg-white/15 text-text' : 'text-text-muted hover:text-text'
              }`}
            >
              <Pencil size={13} />
            </button>
            <button
              type="button"
              aria-pressed={decision === 'reject'}
              aria-label="Reject"
              onClick={() => setDecision('reject')}
              className={`flex h-7 w-7 items-center justify-center rounded-full transition-colors ${
                decision === 'reject' ? 'bg-red-500/90 text-white' : 'text-text-muted hover:text-text'
              }`}
            >
              <X size={14} />
            </button>
          </div>
        ) : (
          <span
            className={`text-xs font-medium ${
              decision === 'reject' ? 'text-red-400' : decision === 'edit' ? 'text-text-muted' : 'text-accent-strong'
            }`}
          >
            {decision === 'reject' ? 'Rejected' : decision === 'edit' ? 'Edited & accepted' : 'Accepted'}
          </span>
        )}
      </div>

      {isEditing ? (
        <div className="mt-4 space-y-3">
          <div>
            <label className="mb-1.5 block text-xs font-medium text-text-muted">Type</label>
            <select
              value={fields.type}
              onChange={(e) => setField('type', e.target.value)}
              className="w-full rounded-lg border border-white/5 bg-input px-3 py-2 text-sm text-text focus:border-accent focus:outline-none"
            >
              {typeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-text-muted">Start</label>
              <input
                type="datetime-local"
                value={fields.start}
                onChange={(e) => setField('start', e.target.value)}
                className="w-full rounded-lg border border-white/5 bg-input px-3 py-2 text-sm text-text focus:border-accent focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-text-muted">End</label>
              <input
                type="datetime-local"
                value={fields.end}
                onChange={(e) => setField('end', e.target.value)}
                className="w-full rounded-lg border border-white/5 bg-input px-3 py-2 text-sm text-text focus:border-accent focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-medium text-text-muted">Location</label>
            <input
              type="text"
              value={fields.location}
              onChange={(e) => setField('location', e.target.value)}
              placeholder="e.g. Ward 5"
              className="w-full rounded-lg border border-white/5 bg-input px-3 py-2 text-sm text-text placeholder:text-text-subtle focus:border-accent focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-medium text-text-muted">Notes</label>
            <textarea
              value={fields.notes}
              onChange={(e) => setField('notes', e.target.value)}
              rows={2}
              className="w-full resize-none rounded-lg border border-white/5 bg-input px-3 py-2 text-sm text-text placeholder:text-text-subtle focus:border-accent focus:outline-none"
            />
          </div>
        </div>
      ) : (
        <div className="mt-3 space-y-1.5">
          {startDate ? (
            <p className={`text-sm font-medium text-text ${decision === 'reject' ? 'line-through decoration-text-subtle' : ''}`}>
              {dateFormat.format(startDate)}
            </p>
          ) : (
            <p className="text-sm text-text-subtle">No date set</p>
          )}

          <p className="text-sm text-text-muted">
            {startDate && endDate ? (
              <>
                {timeFormat.format(startDate)} – {timeFormat.format(endDate)}
                {durationMinutes !== null && durationMinutes > 0 && (
                  <span className="text-text-subtle"> · {formatDuration(durationMinutes)}</span>
                )}
              </>
            ) : startDate ? (
              `Starts ${timeFormat.format(startDate)}`
            ) : (
              'No time set'
            )}
          </p>

          <div className="flex items-center gap-1.5 text-sm text-text-subtle">
            <MapPin size={13} className="shrink-0" />
            <span>{displaySource.location || 'No location'}</span>
          </div>

          {displaySource.notes && (
            <div className="flex items-start gap-1.5 pt-1 text-sm text-text-subtle">
              <StickyNote size={13} className="mt-0.5 shrink-0" />
              <span className="whitespace-pre-wrap">{displaySource.notes}</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
