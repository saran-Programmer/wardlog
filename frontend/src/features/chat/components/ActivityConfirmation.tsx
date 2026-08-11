import { useState } from 'react'
import { ApiError } from '../../../api/client'
import { resumeConversation } from '../../../api/conversations'
import type { ActivityDecision, ActivityDecisionFields, ProposedActivity, SendMessageResponse } from '../../../types/chat'
import { ActivityConfirmationCard, initialCardState, type CardFields, type CardState } from './ActivityConfirmationCard'

interface ActivityConfirmationProps {
  conversationId: string
  activities: ProposedActivity[]
  onResolved: (response: SendMessageResponse) => void
}

function buildFieldsDiff(activity: ProposedActivity, fields: CardFields): ActivityDecisionFields | null {
  const diff: ActivityDecisionFields = {}

  if (fields.type !== activity.type) diff.type = fields.type

  const start = fields.start ? `${fields.start}:00` : ''
  if (start && start !== (activity.start ?? '')) diff.start = start

  const end = fields.end ? `${fields.end}:00` : ''
  if (end && end !== (activity.end ?? '')) diff.end = end

  if (fields.location !== (activity.location ?? '')) diff.location = fields.location
  if (fields.notes !== (activity.notes ?? '')) diff.notes = fields.notes

  return Object.keys(diff).length > 0 ? diff : null
}

export function ActivityConfirmation({ conversationId, activities, onResolved }: ActivityConfirmationProps) {
  const [cardStates, setCardStates] = useState<Record<number, CardState>>(() =>
    Object.fromEntries(activities.map((activity) => [activity.index, initialCardState(activity)])),
  )
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [locked, setLocked] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function updateCard(index: number, next: CardState) {
    setCardStates((prev) => ({ ...prev, [index]: next }))
  }

  async function handleSubmit() {
    setError(null)
    setIsSubmitting(true)

    const decisions: ActivityDecision[] = activities.map((activity) => {
      const card = cardStates[activity.index]

      if (card.decision === 'reject') {
        return { index: activity.index, decision: 'reject' }
      }

      if (card.decision === 'edit') {
        const fields = buildFieldsDiff(activity, card.fields)
        return fields
          ? { index: activity.index, decision: 'edit', fields }
          : { index: activity.index, decision: 'accept' }
      }

      return { index: activity.index, decision: 'accept' }
    })

    try {
      const response = await resumeConversation(conversationId, decisions)
      setLocked(true)
      onResolved(response)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not submit your decisions. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="w-full max-w-xl space-y-3 rounded-2xl border border-white/5 bg-surface p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-text-subtle">
        {locked
          ? 'Reviewed'
          : `Review ${activities.length} proposed ${activities.length === 1 ? 'activity' : 'activities'}`}
      </p>

      <div className="space-y-3">
        {activities.map((activity) => (
          <ActivityConfirmationCard
            key={activity.index}
            activity={activity}
            state={cardStates[activity.index]}
            onChange={(next) => updateCard(activity.index, next)}
            locked={locked}
          />
        ))}
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {!locked && (
        <button
          type="button"
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="w-full rounded-lg bg-accent py-2.5 text-sm font-semibold text-bg transition-opacity hover:opacity-90 disabled:opacity-60"
        >
          {isSubmitting ? 'Submitting…' : 'Confirm decisions'}
        </button>
      )}
    </div>
  )
}
