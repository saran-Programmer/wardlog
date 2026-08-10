import { useEffect, useState } from 'react'
import { IconRail } from '../../components/IconRail'
import { ConversationSidebar } from './components/ConversationSidebar'
import { Composer } from './components/Composer'
import { MessageList } from './components/MessageList'
import { createConversation, getMessages, listConversations, sendMessage } from '../../api/conversations'
import type { Conversation, Message } from '../../types/chat'

export function ChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)

  const [isLoadingConversations, setIsLoadingConversations] = useState(true)
  const [isLoadingMessages, setIsLoadingMessages] = useState(false)
  const [isCreatingConversation, setIsCreatingConversation] = useState(false)
  const [isAwaitingReply, setIsAwaitingReply] = useState(false)
  const [sendError, setSendError] = useState<string | null>(null)

  useEffect(() => {
    listConversations()
      .then(setConversations)
      .catch((err) => console.error('Failed to load conversations', err))
      .finally(() => setIsLoadingConversations(false))
  }, [])

  async function handleSelectConversation(conversationId: string) {
    setActiveConversationId(conversationId)
    setIsLoadingMessages(true)
    try {
      const history = await getMessages(conversationId)
      setMessages(history)
    } catch (err) {
      console.error('Failed to load messages', err)
    } finally {
      setIsLoadingMessages(false)
    }
  }

  async function handleNewChat() {
    if (isCreatingConversation) return
    if (activeConversationId && messages.length === 0) return

    setIsCreatingConversation(true)
    try {
      const { conversation_id } = await createConversation()
      const now = new Date().toISOString()
      setConversations((prev) => [
        { id: conversation_id, doctor_id: '', title: null, created_at: now, updated_at: now },
        ...prev,
      ])
      setActiveConversationId(conversation_id)
      setMessages([])
    } catch (err) {
      console.error('Failed to create conversation', err)
    } finally {
      setIsCreatingConversation(false)
    }
  }

  async function handleSend(text: string, rush: boolean) {
    setSendError(null)

    let conversationId = activeConversationId
    if (!conversationId) {
      setIsCreatingConversation(true)
      try {
        const created = await createConversation()
        conversationId = created.conversation_id
        setActiveConversationId(conversationId)
      } catch (err) {
        console.error('Failed to create conversation', err)
        setIsCreatingConversation(false)
        setSendError('Could not start a new conversation. Please try again.')
        return
      }
      setIsCreatingConversation(false)
    }

    setMessages((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        conversation_id: conversationId!,
        sequence_number: -1,
        role: 'human',
        content: text,
        created_at: new Date().toISOString(),
      },
    ])

    setIsAwaitingReply(true)
    try {
      const response = await sendMessage(conversationId, { message: text, rush, voice_output: false })

      if (response.status === 'reply') {
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            conversation_id: conversationId!,
            sequence_number: -1,
            role: 'ai',
            content: response.reply,
            created_at: new Date().toISOString(),
          },
        ])
      }

      const refreshed = await listConversations()
      setConversations(refreshed)
    } catch (err) {
      console.error('Failed to send message', err)
      setSendError('WardLog could not respond. Please try again.')
    } finally {
      setIsAwaitingReply(false)
    }
  }

  return (
    <div className="flex h-screen bg-bg">
      <IconRail onChatIconClick={() => setIsSidebarOpen((prev) => !prev)} />
      <ConversationSidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        isLoading={isLoadingConversations}
        isCreating={isCreatingConversation}
        isOpen={isSidebarOpen}
        onSelect={handleSelectConversation}
        onNewChat={handleNewChat}
      />

      <div className="flex flex-1 flex-col">
        <MessageList messages={messages} isLoading={isLoadingMessages} isAwaitingReply={isAwaitingReply} />

        {sendError && <p className="px-6 pb-2 text-center text-sm text-red-400">{sendError}</p>}

        <Composer onSend={handleSend} isSending={isAwaitingReply || isCreatingConversation} />
      </div>
    </div>
  )
}
