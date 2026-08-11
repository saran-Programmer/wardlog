import { useEffect, useState } from 'react'
import { IconRail } from '../../components/IconRail'
import { ConversationSidebar } from './components/ConversationSidebar'
import { Composer } from './components/Composer'
import { MessageList, type PendingInterrupt } from './components/MessageList'
import { useSpeechPlayback } from './hooks/useSpeechPlayback'
import {
  createConversation,
  deleteConversation,
  getMessages,
  listConversations,
  renameConversation,
  sendMessage,
  sendVoiceMessage,
} from '../../api/conversations'
import type { Conversation, Message, SendMessageResponse } from '../../types/chat'

export function ChatPage() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [interrupts, setInterrupts] = useState<PendingInterrupt[]>([])
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)

  const [isLoadingConversations, setIsLoadingConversations] = useState(true)
  const [isLoadingMessages, setIsLoadingMessages] = useState(false)
  const [isCreatingConversation, setIsCreatingConversation] = useState(false)
  const [isAwaitingReply, setIsAwaitingReply] = useState(false)
  const [sendError, setSendError] = useState<string | null>(null)

  const speech = useSpeechPlayback()

  useEffect(() => {
    listConversations()
      .then(setConversations)
      .catch((err) => console.error('Failed to load conversations', err))
      .finally(() => setIsLoadingConversations(false))
  }, [])

  async function handleSelectConversation(conversationId: string) {
    setActiveConversationId(conversationId)
    setInterrupts([])
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
      setInterrupts([])
    } catch (err) {
      console.error('Failed to create conversation', err)
    } finally {
      setIsCreatingConversation(false)
    }
  }

  async function handleRenameConversation(conversationId: string, title: string) {
    const previousConversations = conversations
    setConversations((prev) =>
      prev.map((conversation) =>
        conversation.id === conversationId ? { ...conversation, title } : conversation,
      ),
    )

    try {
      await renameConversation(conversationId, title)
    } catch (err) {
      setConversations(previousConversations)
      throw err
    }
  }

  async function handleDeleteConversation(conversationId: string) {
    await deleteConversation(conversationId)

    setConversations((prev) => prev.filter((conversation) => conversation.id !== conversationId))
    if (activeConversationId === conversationId) {
      setActiveConversationId(null)
      setMessages([])
      setInterrupts([])
    }
  }

  async function handleSend(text: string, rush: boolean, viaVoice = false) {
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

    const humanMessageId = crypto.randomUUID()
    setMessages((prev) => [
      ...prev,
      {
        id: humanMessageId,
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
        const aiMessageId = crypto.randomUUID()
        setMessages((prev) => [
          ...prev,
          {
            id: aiMessageId,
            conversation_id: conversationId!,
            sequence_number: -1,
            role: 'ai',
            content: response.reply,
            created_at: new Date().toISOString(),
          },
        ])

        if (viaVoice) {
          speech.play(aiMessageId, response.reply)
        }
      } else {
        setInterrupts((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            conversationId: conversationId!,
            activities: response.payload,
            afterMessageId: humanMessageId,
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

  async function handleSendVoice(audio: Blob, rush: boolean) {
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

    const placeholderId = crypto.randomUUID()
    setMessages((prev) => [
      ...prev,
      {
        id: placeholderId,
        conversation_id: conversationId!,
        sequence_number: -1,
        role: 'human',
        content: '🎤 Voice message',
        created_at: new Date().toISOString(),
      },
    ])

    setIsAwaitingReply(true)
    try {
      const response = await sendVoiceMessage(conversationId, audio, rush)

      if (response.status === 'reply') {
        const history = await getMessages(conversationId)
        setMessages(history)

        const lastMessage = history[history.length - 1]
        if (lastMessage && lastMessage.role === 'ai') {
          speech.play(lastMessage.id, lastMessage.content)
        }
      } else {
        setInterrupts((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            conversationId: conversationId!,
            activities: response.payload,
            afterMessageId: placeholderId,
          },
        ])
      }

      const refreshed = await listConversations()
      setConversations(refreshed)
    } catch (err) {
      console.error('Failed to send voice message', err)
      setSendError('WardLog could not respond. Please try again.')
      setMessages((prev) => prev.filter((message) => message.id !== placeholderId))
    } finally {
      setIsAwaitingReply(false)
    }
  }

  async function handleInterruptResolved(interrupt: PendingInterrupt, response: SendMessageResponse) {
    if (response.status === 'reply') {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          conversation_id: interrupt.conversationId,
          sequence_number: -1,
          role: 'ai',
          content: response.reply,
          created_at: new Date().toISOString(),
        },
      ])
    } else {
      setInterrupts((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          conversationId: interrupt.conversationId,
          activities: response.payload,
          afterMessageId: interrupt.afterMessageId,
        },
      ])
    }

    try {
      const refreshed = await listConversations()
      setConversations(refreshed)
    } catch (err) {
      console.error('Failed to refresh conversations', err)
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
        onRename={handleRenameConversation}
        onDelete={handleDeleteConversation}
      />

      <div className="flex flex-1 flex-col">
        <MessageList
          messages={messages}
          interrupts={interrupts}
          isLoading={isLoadingMessages}
          isAwaitingReply={isAwaitingReply}
          speechActiveId={speech.activeId}
          speechStatus={speech.status}
          onToggleSpeech={speech.play}
          onInterruptResolved={handleInterruptResolved}
        />

        {sendError && <p className="px-6 pb-2 text-center text-sm text-red-400">{sendError}</p>}

        <Composer
          onSend={handleSend}
          onSendVoice={handleSendVoice}
          onMicUnlock={speech.unlock}
          isSending={isAwaitingReply || isCreatingConversation}
        />
      </div>
    </div>
  )
}
