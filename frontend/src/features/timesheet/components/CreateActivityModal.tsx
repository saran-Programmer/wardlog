import { useState } from 'react'
import { X } from 'lucide-react'
import { Input } from '../../../components/Input'
import { createActivity } from '../../../api/activities'
import { ApiError } from '../../../api/client'
import { ACTIVITY_TYPE_OPTIONS } from '../../../lib/activityType'
import { combineDateAndTime, toDateInputValue, toLocalDateTimeString, toTimeInputValue } from '../../../lib/date'
import type { ActivityResponse, ActivityType } from '../../../types/timesheet'

const headingDateFormat = new Intl.DateTimeFormat('en-US', {
  weekday: 'long',
  month: 'long',
  day: 'numeric',
  year: 'numeric',
})
const headingTimeFormat = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit' })

interface CreateActivityModalProps {
  doctorId: string
  start: Date
  end: Date
  onClose: () => void
  onCreated: (activity: ActivityResponse) => void
}

export function CreateActivityModal({ doctorId, start, end, onClose, onCreated }: CreateActivityModalProps) {
  const [activityType, setActivityType] = useState<ActivityType>(ACTIVITY_TYPE_OPTIONS[0].value)
  const [dateValue, setDateValue] = useState(toDateInputValue(start))
  const [startTimeValue, setStartTimeValue] = useState(toTimeInputValue(start))
  const [endTimeValue, setEndTimeValue] = useState(toTimeInputValue(end))
  const [location, setLocation] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  const previewStart = combineDateAndTime(dateValue, startTimeValue)
  const previewEnd = combineDateAndTime(dateValue, endTimeValue)

  async function handleSave() {
    if (previewEnd <= previewStart) {
      setError('End time must be after start time')
      return
    }

    setError(null)
    setIsSaving(true)

    try {
      const activity = await createActivity({
        doctorId,
        activityType,
        startDateTime: toLocalDateTimeString(previewStart),
        endDateTime: toLocalDateTimeString(previewEnd),
        location: location || undefined,
        notes: notes || undefined,
      })

      onCreated(activity)
      onClose()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Unable to log this activity. Please try again.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-lg rounded-2xl border border-white/5 bg-surface p-6">
        <div className="mb-1 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-text">Log Activity</h2>
          <button type="button" onClick={onClose} aria-label="Close" className="text-text-muted hover:text-text">
            <X size={18} />
          </button>
        </div>

        <p className="mb-5 text-sm text-text-muted">
          {headingDateFormat.format(previewStart)} · {headingTimeFormat.format(previewStart)} –{' '}
          {headingTimeFormat.format(previewEnd)}
        </p>

        <div className="space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-text-muted">Activity Type</label>
            <select
              value={activityType}
              onChange={(e) => setActivityType(e.target.value as ActivityType)}
              className="w-full rounded-lg border border-white/5 bg-input px-4 py-2.5 text-text focus:border-accent focus:outline-none"
            >
              {ACTIVITY_TYPE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1.5 block text-sm font-medium text-text-muted">Date</label>
            <input
              type="date"
              value={dateValue}
              onChange={(e) => setDateValue(e.target.value)}
              className="w-full rounded-lg border border-white/5 bg-input px-4 py-2.5 text-text focus:border-accent focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-text-muted">Start</label>
              <input
                type="time"
                value={startTimeValue}
                onChange={(e) => setStartTimeValue(e.target.value)}
                className="w-full rounded-lg border border-white/5 bg-input px-4 py-2.5 text-text focus:border-accent focus:outline-none"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-text-muted">End</label>
              <input
                type="time"
                value={endTimeValue}
                onChange={(e) => setEndTimeValue(e.target.value)}
                className="w-full rounded-lg border border-white/5 bg-input px-4 py-2.5 text-text focus:border-accent focus:outline-none"
              />
            </div>
          </div>

          <Input label="Location" placeholder="e.g. OR 4" value={location} onChange={(e) => setLocation(e.target.value)} />

          <div>
            <label className="mb-1.5 block text-sm font-medium text-text-muted">Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              className="w-full resize-none rounded-lg border border-white/5 bg-input px-4 py-2.5 text-text placeholder:text-text-subtle focus:border-accent focus:outline-none"
            />
          </div>

          {error && <p className="text-sm text-red-400">{error}</p>}
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-white/10 px-4 py-2 text-sm font-medium text-text hover:bg-white/5"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            disabled={isSaving}
            className="rounded-lg bg-accent px-5 py-2 text-sm font-semibold text-bg transition-opacity hover:opacity-90 disabled:opacity-60"
          >
            {isSaving ? 'Posting…' : 'Post Activity'}
          </button>
        </div>
      </div>
    </div>
  )
}
