import { useEffect, useState } from 'react'
import { MapPin, Paperclip, X } from 'lucide-react'
import { getActivityById } from '../../../api/activities'
import { ApiError } from '../../../api/client'
import { getActivityTypeOption } from '../../../lib/activityType'
import { formatDuration } from '../../../lib/date'
import { formatFileSize } from '../../../lib/format'
import type { ActivityResponse } from '../../../types/timesheet'

const dateFormat = new Intl.DateTimeFormat('en-US', {
  weekday: 'long',
  month: 'long',
  day: 'numeric',
  year: 'numeric',
})
const timeFormat = new Intl.DateTimeFormat('en-US', { hour: 'numeric', minute: '2-digit' })

interface ActivityDetailDrawerProps {
  activityId: string
  onClose: () => void
}

export function ActivityDetailDrawer({ activityId, onClose }: ActivityDetailDrawerProps) {
  const [activity, setActivity] = useState<ActivityResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setActivity(null)
    setError(null)
    setIsLoading(true)

    getActivityById(activityId)
      .then((response) => {
        if (!cancelled) setActivity(response)
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof ApiError ? err.message : 'Unable to load this activity.')
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [activityId])

  const option = activity ? getActivityTypeOption(activity.activityType) : null
  const start = activity ? new Date(activity.startDateTime) : null
  const end = activity ? new Date(activity.endDateTime) : null

  return (
    <div className="fixed inset-0 z-30 flex justify-end bg-black/60" onClick={onClose}>
      <div
        className="flex h-full w-full max-w-md flex-col overflow-y-auto border-l border-white/5 bg-surface p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-text">Activity Detail</h2>
          <button type="button" onClick={onClose} aria-label="Close" className="text-text-muted hover:text-text">
            <X size={18} />
          </button>
        </div>

        {isLoading && <p className="text-sm text-text-muted">Loading…</p>}
        {error && <p className="text-sm text-red-400">{error}</p>}

        {activity && option && start && end && (
          <div className="space-y-5">
            <span className={`inline-block rounded-full px-3 py-1 text-sm font-semibold text-bg ${option.chipBg}`}>
              {option.label}
            </span>

            <div>
              <p className="text-base font-semibold text-text">{dateFormat.format(start)}</p>
              <p className="mt-1 text-sm text-text-muted">
                {timeFormat.format(start)} – {timeFormat.format(end)} · {formatDuration(activity.durationMinutes)}
              </p>
            </div>

            {activity.location && (
              <div className="flex items-center gap-2 text-sm text-text-muted">
                <MapPin size={16} />
                {activity.location}
              </div>
            )}

            {activity.notes && <p className="rounded-lg bg-input px-4 py-3 text-sm text-text">{activity.notes}</p>}

            {activity.consultations && activity.consultations.some((c) => c.patient?.name) && (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-text-subtle">
                  Linked Patients
                </p>
                <div className="space-y-2">
                  {activity.consultations
                    .filter((consultation) => consultation.patient?.name)
                    .map((consultation, index) => (
                      <div key={index} className="rounded-lg bg-surface-raised p-3">
                        <p className="text-sm font-semibold text-text">
                          {consultation.patient!.name}
                          {consultation.patient!.age != null && (
                            <span className="font-normal text-text-muted"> · {consultation.patient!.age} yrs</span>
                          )}
                        </p>
                        {consultation.diagnoses.length > 0 && (
                          <p className="mt-1 text-xs text-text-muted">
                            Diagnosis: <span className="text-text">{consultation.diagnoses.join(', ')}</span>
                          </p>
                        )}
                        {consultation.drugs.length > 0 && (
                          <p className="mt-0.5 text-xs text-text-muted">
                            Drugs: <span className="text-text">{consultation.drugs.join(', ')}</span>
                          </p>
                        )}
                      </div>
                    ))}
                </div>
              </div>
            )}

            {activity.documents && activity.documents.length > 0 && (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-text-subtle">Documents</p>
                <div className="space-y-2">
                  {activity.documents.map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center justify-between rounded-lg bg-surface-raised px-4 py-2.5"
                    >
                      <div className="flex items-center gap-2 text-sm text-text">
                        <Paperclip size={14} className="text-text-subtle" />
                        {doc.fileName}
                      </div>
                      <span className="text-xs text-text-subtle">{formatFileSize(doc.fileSizeBytes)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                className="rounded-lg bg-accent px-5 py-2 text-sm font-semibold text-bg hover:opacity-90"
              >
                Edit
              </button>
              <button
                type="button"
                className="rounded-lg border border-red-500/30 px-5 py-2 text-sm font-semibold text-red-400 hover:bg-red-500/10"
              >
                Delete
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
