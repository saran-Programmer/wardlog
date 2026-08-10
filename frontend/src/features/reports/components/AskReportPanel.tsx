import { useState } from 'react'
import { MessageSquare, Send } from 'lucide-react'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  text: string
}

const suggestions = ['Breakdown & trend', 'Any gaps?']

const NOT_AVAILABLE_TEXT = "Asking about reports isn't available yet — this feature is still being built."

export function AskReportPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')

  function sendMessage(text: string) {
    const trimmed = text.trim()
    if (!trimmed) return

    setMessages((prev) => [
      ...prev,
      { id: crypto.randomUUID(), role: 'user', text: trimmed },
      { id: crypto.randomUUID(), role: 'assistant', text: NOT_AVAILABLE_TEXT },
    ])
    setInput('')
  }

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    sendMessage(input)
  }

  return (
    <div className="flex w-[340px] flex-none flex-col rounded-xl border border-white/10 bg-surface p-5">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 flex-none items-center justify-center rounded-lg bg-accent-muted text-accent-strong">
          <MessageSquare size={16} />
        </div>
        <p className="font-semibold text-text">Ask about this report</p>
      </div>

      <div className="calendar-scroll mt-4 flex min-h-0 flex-1 flex-col gap-3 overflow-y-auto pr-1">
        <p className="text-sm text-text-muted">
          I can answer questions about the activities in this report. Try a suggestion below, or tap a bar to see
          the entries behind it.
        </p>

        {messages.map((message) =>
          message.role === 'user' ? (
            <div key={message.id} className="ml-auto max-w-[85%] rounded-lg bg-accent-muted px-3 py-2 text-sm text-text">
              {message.text}
            </div>
          ) : (
            <div key={message.id} className="max-w-[85%] rounded-lg bg-surface-raised px-3 py-2 text-sm text-text-muted">
              {message.text}
            </div>
          ),
        )}
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            type="button"
            onClick={() => sendMessage(suggestion)}
            className="rounded-lg bg-surface-raised px-3 py-1.5 text-sm font-medium text-text-muted hover:text-text"
          >
            {suggestion}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="mt-3 flex items-center gap-2">
        <input
          type="text"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask a question…"
          className="min-w-0 flex-1 rounded-lg bg-input px-3 py-2 text-sm text-text placeholder:text-text-subtle focus:outline-none"
        />
        <button
          type="submit"
          aria-label="Send"
          className="flex h-9 w-9 flex-none items-center justify-center rounded-lg bg-accent text-bg transition-opacity hover:opacity-90"
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  )
}
