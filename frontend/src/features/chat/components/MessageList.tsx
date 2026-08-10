import { useEffect, useRef } from 'react'
import type { Message } from '../../../types/chat'

interface MessageListProps {
  messages: Message[]
  isLoading: boolean
  isAwaitingReply: boolean
}

export function MessageList({ messages, isLoading, isAwaitingReply }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: 'end' })
  }, [messages.length, isAwaitingReply])

  if (isLoading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-text-subtle">Loading conversation…</p>
      </div>
    )
  }

  if (messages.length === 0 && !isAwaitingReply) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-text-subtle">Tell WardLog what you did today to get started.</p>
      </div>
    )
  }

  return (
    <div className="flex flex-1 flex-col gap-3 overflow-y-auto px-6 py-6">
      {messages.map((message) => (
        <div key={message.id} className={`flex ${message.role === 'human' ? 'justify-end' : 'justify-start'}`}>
          <div
            className={`max-w-[65%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm ${
              message.role === 'human' ? 'bg-accent-muted text-text' : 'bg-surface-raised text-text'
            }`}
          >
            {message.content}
          </div>
        </div>
      ))}

      {isAwaitingReply && (
        <div className="flex justify-start">
          <div className="flex items-center gap-1.5 rounded-2xl bg-surface-raised px-4 py-3.5">
            <span className="h-2 w-2 animate-bounce rounded-full bg-text-muted [animation-delay:-0.3s]" />
            <span className="h-2 w-2 animate-bounce rounded-full bg-text-muted [animation-delay:-0.15s]" />
            <span className="h-2 w-2 animate-bounce rounded-full bg-text-muted" />
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  )
}
