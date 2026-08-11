import { useEffect, useRef } from 'react'
import { Loader2, Volume2, VolumeX } from 'lucide-react'
import type { Message } from '../../../types/chat'
import type { SpeechStatus } from '../hooks/useSpeechPlayback'

interface MessageListProps {
  messages: Message[]
  isLoading: boolean
  isAwaitingReply: boolean
  speechActiveId: string | null
  speechStatus: SpeechStatus
  onToggleSpeech: (id: string, text: string) => void
}

export function MessageList({
  messages,
  isLoading,
  isAwaitingReply,
  speechActiveId,
  speechStatus,
  onToggleSpeech,
}: MessageListProps) {
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
      {messages.map((message) => {
        const isAi = message.role === 'ai'
        const state: SpeechStatus = isAi && speechActiveId === message.id ? speechStatus : 'idle'

        return (
          <div key={message.id} className={`flex ${message.role === 'human' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[65%] rounded-2xl px-4 py-2.5 text-sm ${
                message.role === 'human' ? 'bg-accent-muted text-text' : 'bg-surface-raised text-text'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>

              {isAi && (
                <div className="mt-1.5 flex justify-end">
                  <button
                    type="button"
                    aria-label={
                      state === 'playing'
                        ? 'Stop playback'
                        : state === 'loading'
                          ? 'Generating audio…'
                          : state === 'error'
                            ? 'Playback failed'
                            : 'Play message aloud'
                    }
                    onClick={() => onToggleSpeech(message.id, message.content)}
                    disabled={state === 'loading'}
                    className={`flex h-6 w-6 items-center justify-center rounded-full text-text-subtle transition-colors hover:text-text disabled:opacity-70 ${
                      state === 'playing' ? 'text-accent-strong' : ''
                    } ${state === 'error' ? 'text-red-400' : ''}`}
                  >
                    {state === 'loading' && <Loader2 size={14} className="animate-spin" />}
                    {state === 'error' && <VolumeX size={14} />}
                    {(state === 'idle' || state === 'playing') && <Volume2 size={14} />}
                  </button>
                </div>
              )}
            </div>
          </div>
        )
      })}

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
