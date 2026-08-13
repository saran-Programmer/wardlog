export type MessageRole = 'human' | 'ai' | 'assistant'
export type EventStatus = 'pending' | 'accepted' | 'rejected' | null

export interface Conversation {
  id: string
  doctor_id: string
  title: string | null
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  conversation_id: string
  sequence_number: number
  role: MessageRole
  content: string
  created_at: string
  event_status: EventStatus
}

export interface CreateConversationResponse {
  conversation_id: string
}

export interface RenameConversationResponse {
  conversation_id: string
  title: string
}

export interface SendMessageRequest {
  message: string
  rush: boolean
  voice_output: boolean
}

export interface SendMessageReply {
  status: 'reply'
  reply: string
  audio_base64: string | null
}

export interface ProposedActivity {
  id: string
  type: string
  start: string | null
  end: string | null
  location: string | null
  notes: string | null
}

export interface SendMessageConfirmationInterrupt {
  status: 'interrupt'
  interrupt_type: 'confirmation'
  activities: ProposedActivity[]
}

export interface DisambiguationOption {
  index: number
  id: string
  type: string
  start: string | null
  end: string | null
  location: string | null
  notes: string | null
}

export interface SendMessageDisambiguationInterrupt {
  status: 'interrupt'
  interrupt_type: 'disambiguation'
  options: DisambiguationOption[]
  allow_query: boolean
}

export type SendMessageInterrupt = SendMessageConfirmationInterrupt | SendMessageDisambiguationInterrupt

export type SendMessageResponse = SendMessageReply | SendMessageInterrupt

export type ActivityDecisionKind = 'accept' | 'reject' | 'edit'

export interface ActivityDecisionFields {
  type?: string
  start?: string
  end?: string
  location?: string
  notes?: string
}

export interface ActivityDecision {
  id: string
  decision: ActivityDecisionKind
  fields?: ActivityDecisionFields
}

export interface ConfirmationResumeRequest {
  decisions: ActivityDecision[]
}

// Sentinel `choice` value: doctor sent a follow-up question instead of
// picking one of the presented disambiguation options.
export const DISAMBIGUATION_QUERY_CHOICE = 'query' as const

export interface DisambiguationResumeRequest {
  choice: string
  query_text?: string
}
