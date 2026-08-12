import { useMemo, useState } from 'react'
import { ApiError } from '../../../api/client'
import { resumeConversation } from '../../../api/conversations'
import type {
  ActivityDecision,
  ActivityDecisionFields,
  EventStatus,
  Message,
  ProposedActivity,
  SendMessageResponse,
} from '../../../types/chat'
import {
  ActivityConfirmationCard,
  initialCardState,
  resolvedCardState,
  type CardFields,
  type CardState,
} from './ActivityConfirmationCard'

export interface ResolvedActivityUpdate {
  id: string
  event_status: 'accepted' | 'rejected'
  content: string
}

interface ActivityConfirmationProps {
  conversationId: string
  messages: Message[]
  onResolved: (updates: ResolvedActivityUpdate[], response: SendMessageResponse) => void
}

function toProposedActivity(message: Message): ProposedActivity {
  const data = JSON.parse(message.content) as {
    type: string
    start: string | null
    end: string | null
    location: string | null
    notes: string | null
  }
  return {
    id: message.id,
    type: data.type,
    start: data.start,
    end: data.end,
    location: data.location,
    notes: data.notes,
  }
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

function finalActivityContent(activity: ProposedActivity, card: CardState): string {
  if (card.decision === 'edit') {
    return JSON.stringify({
      type: card.fields.type,
      start: card.fields.start ? `${card.fields.start}:00` : activity.start,
      end: card.fields.end ? `${card.fields.end}:00` : activity.end,
      location: card.fields.location || null,
      notes: card.fields.notes || null,
    })
  }

  return JSON.stringify({
    type: activity.type,
    start: activity.start,
    end: activity.end,
    location: activity.location,
    notes: activity.notes,
  })
}

export function ActivityConfirmation({ conversationId, messages, onResolved }: ActivityConfirmationProps) {
  const activities = useMemo(() => messages.map(toProposedActivity), [messages])
  const statusById = useMemo(
    () => new Map<string, EventStatus>(messages.map((message) => [message.id, message.event_status])),
    [messages],
  )
  const isPending = messages[0]?.event_status === 'pending'

  const [cardStates, setCardStates] = useState<Record<string, CardState>>(() =>
    Object.fromEntries(
      activities.map((activity) => {
        const status = statusById.get(activity.id)
        const state =
          status === 'accepted' || status === 'rejected'
            ? resolvedCardState(activity, status)
            : initialCardState(activity)
        return [activity.id, state]
      }),
    ),
  )
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function updateCard(id: string, next: CardState) {
    setCardStates((prev) => ({ ...prev, [id]: next }))
  }

  async function handleSubmit() {
    setError(null)
    setIsSubmitting(true)

    const decisions: ActivityDecision[] = activities.map((activity) => {
      const card = cardStates[activity.id]

      if (card.decision === 'reject') {
        return { id: activity.id, decision: 'reject' }
      }

      if (card.decision === 'edit') {
        const fields = buildFieldsDiff(activity, card.fields)
        return fields
          ? { id: activity.id, decision: 'edit', fields }
          : { id: activity.id, decision: 'accept' }
      }

      return { id: activity.id, decision: 'accept' }
    })

    try {
      const response = await resumeConversation(conversationId, decisions)
      const updates: ResolvedActivityUpdate[] = activities.map((activity) => ({
        id: activity.id,
        event_status: cardStates[activity.id].decision === 'reject' ? 'rejected' : 'accepted',
        content: finalActivityContent(activity, cardStates[activity.id]),
      }))
      onResolved(updates, response)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not submit your decisions. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="w-full max-w-xl space-y-3 rounded-2xl border border-white/5 bg-surface p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-text-subtle">
        {!isPending
          ? 'Reviewed'
          : `Review ${activities.length} proposed ${activities.length === 1 ? 'activity' : 'activities'}`}
      </p>

      <div className="space-y-3">
        {activities.map((activity) => (
          <ActivityConfirmationCard
            key={activity.id}
            activity={activity}
            state={cardStates[activity.id]}
            onChange={(next) => updateCard(activity.id, next)}
            locked={!isPending}
          />
        ))}
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      {isPending && (
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
