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
