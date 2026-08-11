import { apiRequest } from './client'
import type {
  Conversation,
  CreateConversationResponse,
  Message,
  SendMessageRequest,
  SendMessageResponse,
} from '../types/chat'

export function listConversations(): Promise<Conversation[]> {
  return apiRequest<Conversation[]>('/api/v1/conversations')
}

export function createConversation(): Promise<CreateConversationResponse> {
  return apiRequest<CreateConversationResponse>('/api/v1/conversations', {
    method: 'POST',
  })
}

export function getMessages(conversationId: string): Promise<Message[]> {
  return apiRequest<Message[]>(`/api/v1/conversations/${conversationId}/messages`)
}

export function sendMessage(
  conversationId: string,
  request: SendMessageRequest,
): Promise<SendMessageResponse> {
  return apiRequest<SendMessageResponse>(`/api/v1/conversations/${conversationId}/messages`, {
    method: 'POST',
    body: request,
  })
}

export function sendVoiceMessage(
  conversationId: string,
  audio: Blob,
  rush: boolean,
): Promise<SendMessageResponse> {
  const formData = new FormData()
  formData.append('audio', audio, 'voice-message.webm')
  formData.append('rush', String(rush))

  return apiRequest<SendMessageResponse>(`/api/v1/conversations/${conversationId}/voice-message`, {
    method: 'POST',
    body: formData,
  })
}
