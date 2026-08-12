import { apiRequest } from './client'
import type {
  ActivityDecision,
  Conversation,
  CreateConversationResponse,
  Message,
  RenameConversationResponse,
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

export function renameConversation(
  conversationId: string,
  title: string,
): Promise<RenameConversationResponse> {
  return apiRequest<RenameConversationResponse>(`/api/v1/conversations/${conversationId}`, {
    method: 'PUT',
    body: { title },
  })
}

export function deleteConversation(conversationId: string): Promise<void> {
  return apiRequest<void>(`/api/v1/conversations/${conversationId}`, {
    method: 'DELETE',
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

export function sendDocument(
  conversationId: string,
  file: File,
  message: string,
  rush: boolean,
): Promise<SendMessageResponse> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('message', message)
  formData.append('rush', String(rush))

  return apiRequest<SendMessageResponse>(`/api/v1/conversations/${conversationId}/documents`, {
    method: 'POST',
    body: formData,
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

export function resumeConversation(
  conversationId: string,
  decisions: ActivityDecision[],
): Promise<SendMessageResponse> {
  return apiRequest<SendMessageResponse>(`/api/v1/conversations/${conversationId}/resume`, {
    method: 'POST',
    body: { decisions },
  })
}

export function resumeDisambiguation(
  conversationId: string,
  choice: string,
  queryText?: string,
): Promise<SendMessageResponse> {
  return apiRequest<SendMessageResponse>(`/api/v1/conversations/${conversationId}/resume`, {
    method: 'POST',
    body: { choice, query_text: queryText },
  })
}
